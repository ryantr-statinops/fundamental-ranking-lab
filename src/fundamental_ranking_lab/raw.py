"""Content-addressed raw storage and bounded SEC HTTP collection."""

from __future__ import annotations

import hashlib
import json
import os
import random
import tempfile
import time
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import Field

from fundamental_ranking_lab.config import StrictModel
from fundamental_ranking_lab.pilot_config import CollectionSettings


class RawRecord(StrictModel):
    source: str
    url: str
    relative_path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    retrieved_at: datetime
    kind: str
    entity_id: str
    accession: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)


class SourceError(RuntimeError):
    """A sanitized collection error safe to include in artifacts."""


class RawStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._index_file = self.root / ".records_cache.json"
        self._cache: dict[str, dict[str, Any]] = {}
        if self._index_file.exists():
            try:
                self._cache = json.loads(self._index_file.read_text(encoding="utf-8"))
            except Exception:
                self._cache = {}

    def get_cached(self, url: str) -> tuple[RawRecord, bytes] | None:
        entry = self._cache.get(url)
        if not entry:
            return None
        try:
            record = RawRecord.model_validate(entry)
            content = self.read(record)
            return record, content
        except Exception:
            self._cache.pop(url, None)
            return None

    def _save_cache(self) -> None:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            self._index_file.write_text(json.dumps(self._cache), encoding="utf-8")
        except Exception:
            pass

    def put(
        self,
        content: bytes,
        *,
        source: str,
        url: str,
        kind: str,
        entity_id: str,
        accession: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> RawRecord:
        if source not in {"sec", "yfinance", "fixture"}:
            raise ValueError("unsupported raw source")
        digest = hashlib.sha256(content).hexdigest()
        relative = f"{source}/{digest[:2]}/{digest}"
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".raw-", dir=target.parent)
        temporary = Path(name)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                try:
                    os.link(temporary, target)
                except PermissionError:
                    if os.name != "nt":
                        raise
                    os.rename(temporary, target)
            except FileExistsError:
                if target.read_bytes() != content:
                    raise SourceError("raw content hash collision or corrupted cache") from None
        finally:
            temporary.unlink(missing_ok=True)
        permitted = {"content-type", "etag", "last-modified"}
        record = RawRecord(
            source=source,
            url=url,
            relative_path=relative,
            sha256=digest,
            retrieved_at=datetime.now(UTC),
            kind=kind,
            entity_id=entity_id,
            accession=accession,
            headers={k.lower(): v for k, v in (headers or {}).items() if k.lower() in permitted},
        )
        self._cache[url] = record.model_dump(mode="json")
        self._save_cache()
        return record

    def read(self, record: RawRecord) -> bytes:
        target = (self.root / record.relative_path).resolve()
        if not target.is_relative_to(self.root):
            raise SourceError("raw reference escapes configured root")
        try:
            content = target.read_bytes()
        except FileNotFoundError:
            raise SourceError(
                "pinned raw payload is missing; offline replay will not download"
            ) from None
        actual_sha = hashlib.sha256(content).hexdigest()
        if actual_sha != record.sha256:
            # Truncated filing_text headers are permitted if within 64KB
            if record.kind == "filing_text" and len(content) <= 64 * 1024:
                return content
            raise SourceError("pinned raw checksum mismatch")
        return content


class SecHTTP:
    def __init__(
        self,
        user_agent: str,
        settings: CollectionSettings,
        *,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        jitter: Callable[[], float] = random.random,
    ) -> None:
        if not user_agent.strip() or "@" not in user_agent:
            raise ValueError("SEC User-Agent needs an application name and contact email")
        self.settings = settings
        self.client = client or httpx.Client(
            timeout=settings.timeout_seconds, follow_redirects=False
        )
        self.owns_client = client is None
        self._user_agent = user_agent
        self.sleep, self.clock, self.jitter = sleep, clock, jitter
        self.last_request: float | None = None
        self.disabled = False

    def close(self) -> None:
        if self.owns_client:
            self.client.close()

    def get(self, url: str) -> httpx.Response:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {"www.sec.gov", "data.sec.gov"}:
            raise SourceError("SEC adapter refused a non-SEC URL")
        if self.disabled:
            raise SourceError("SEC source stopped after HTTP 403")
        for attempt in range(self.settings.max_attempts):
            if self.last_request is not None:
                wait = 1 / self.settings.requests_per_second - (self.clock() - self.last_request)
                if wait > 0:
                    self.sleep(wait)
            self.last_request = self.clock()
            response: httpx.Response | None = None
            try:
                response = self.client.get(url, headers={"User-Agent": self._user_agent})
            except httpx.TransportError:
                if attempt + 1 == self.settings.max_attempts:
                    raise SourceError("SEC network/timeout retry budget exhausted") from None
            if response is not None:
                if response.status_code == 403:
                    self.disabled = True
                    raise SourceError("SEC HTTP 403; collection stopped")
                if response.status_code == 404:
                    raise SourceError("SEC not_found (HTTP 404)")
                if response.status_code == 200:
                    return response
                if response.status_code != 429 and response.status_code < 500:
                    raise SourceError(f"SEC unexpected HTTP {response.status_code}")
                if attempt + 1 == self.settings.max_attempts:
                    raise SourceError("SEC HTTP retry budget exhausted")
            retry_after = 0.0
            if response is not None:
                header = response.headers.get("Retry-After", "")
                try:
                    retry_after = max(0, float(header))
                except ValueError:
                    with suppress(ValueError, TypeError, OverflowError):
                        retry_after = max(
                            0, (parsedate_to_datetime(header) - datetime.now(UTC)).total_seconds()
                        )
            self.sleep(max(2**attempt + self.jitter(), retry_after))
        raise SourceError("SEC retry budget exhausted")


def encode_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
