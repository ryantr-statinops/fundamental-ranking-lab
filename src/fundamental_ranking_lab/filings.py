"""Read original XBRL/inline-XBRL contexts, preserving reported evidence."""

from __future__ import annotations

import re
from contextlib import suppress
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Literal
from zoneinfo import ZoneInfo

from lxml import etree  # type: ignore[import-untyped]

from fundamental_ranking_lab.config import StrictModel


class FilingHeader(StrictModel):
    accession: str
    filed_date: date
    published_at: datetime | None = None
    form: str
    sic: str | None = None


class Fact(StrictModel):
    entity_id: str
    accession: str
    taxonomy: str
    tag: str
    context_id: str
    period_start: date | None = None
    period_end: date
    unit: str | None = None
    value_text: str
    value: Decimal | None = None
    scale: int = 0
    decimals: str | None = None
    dimensions: tuple[tuple[str, str], ...] = ()
    filed_date: date
    published_at: datetime | None = None
    publication_precision: Literal["timestamp", "date_only"]
    raw_sha256: str
    form: str
    document_period_end: date | None = None

    def available(self, cutoff: datetime) -> bool:
        if cutoff.tzinfo is None:
            raise ValueError("cutoff must be timezone-aware")
        if self.published_at is not None:
            if self.published_at.tzinfo is None:
                raise ValueError("publication must be timezone-aware")
            return self.published_at <= cutoff
        return self.filed_date < cutoff.astimezone(ZoneInfo("America/New_York")).date()


def parse_header(content: bytes, accession: str) -> FilingHeader:
    text = content.decode("utf-8", errors="replace")
    filed = re.search(r"(?:FILED AS OF DATE:\s*|<FILED-AS-OF-DATE>)(\d{8})", text)
    accepted = re.search(r"<ACCEPTANCE-DATETIME>(\d{14})", text)
    form = re.search(
        r"(?:CONFORMED SUBMISSION TYPE:\s*|<CONFORMED-SUBMISSION-TYPE>)([\w/-]+)", text
    )
    sic = re.search(r"STANDARD INDUSTRIAL CLASSIFICATION:[^\n]*\[(\d{4})\]", text)
    if filed is None or form is None:
        raise ValueError("original SEC filing header lacks filed date or form")
    published = None
    if accepted:
        published = (
            datetime.strptime(accepted[1], "%Y%m%d%H%M%S")
            .replace(tzinfo=ZoneInfo("America/New_York"))
            .astimezone(UTC)
        )
    return FilingHeader(
        accession=accession,
        filed_date=datetime.strptime(filed[1], "%Y%m%d").date(),
        published_at=published,
        form=form[1],
        sic=sic[1] if sic else None,
    )


def _local(tag: object) -> str:
    return str(tag).rsplit("}", 1)[-1].split(":")[-1].lower()


def _attr(element: etree._Element, name: str) -> str | None:
    for key, value in element.attrib.items():
        if _local(key) == name.lower():
            return str(value)
    return None


def _text(element: etree._Element) -> str:
    return "".join(element.itertext()).strip()


def parse_document(
    content: bytes,
    *,
    entity_id: str,
    cik: str,
    header: FilingHeader,
    raw_sha256: str,
) -> tuple[list[Fact], list[str]]:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False)
    try:
        root = etree.fromstring(content, parser)
    except etree.XMLSyntaxError:
        root = etree.fromstring(content, etree.HTMLParser(no_network=True))
    if root is None:
        return [], ["filing_document_unparseable"]
    contexts: dict[str, tuple[date | None, date, tuple[tuple[str, str], ...]]] = {}
    units: dict[str, str] = {}
    issues: list[str] = []
    for element in root.iter():
        local = _local(element.tag)
        identifier = _attr(element, "id")
        if local == "context" and identifier:
            values: dict[str, str] = {}
            dimensions = []
            for child in element.iter():
                child_name = _local(child.tag)
                if child_name in {"identifier", "startdate", "enddate", "instant"}:
                    values[child_name] = _text(child)
                elif child_name in {"explicitmember", "typedmember"}:
                    dimensions.append((_attr(child, "dimension") or "unknown", _text(child)))
            reported_cik = values.get("identifier", "").lstrip("0")
            if reported_cik != cik.lstrip("0"):
                issues.append("context_entity_mismatch")
                continue
            try:
                start = date.fromisoformat(values["startdate"]) if "startdate" in values else None
                end = date.fromisoformat(values.get("instant") or values["enddate"])
                contexts[identifier] = (start, end, tuple(sorted(dimensions)))
            except (ValueError, KeyError):
                issues.append("invalid_context_period")
        elif local == "unit" and identifier:
            measures = [
                _text(child).split(":")[-1]
                for child in element.iter()
                if _local(child.tag) == "measure"
            ]
            if measures:
                units[identifier] = "/".join(measures)
    document_end = None
    for element in root.iter():
        name = _attr(element, "name") or str(element.tag)
        if name.rsplit("}", 1)[-1].split(":")[-1] == "DocumentPeriodEndDate":
            with suppress(ValueError):
                document_end = date.fromisoformat(_text(element))
    facts = []
    for element in root.iter():
        context_id = _attr(element, "contextRef")
        if not context_id or context_id not in contexts:
            continue
        if _local(element.tag) in {"nonfraction", "nonnumeric", "fraction"}:
            name = _attr(element, "name") or ""
            taxonomy, _, tag = name.partition(":")
        else:
            tag = str(element.tag).rsplit("}", 1)[-1].split(":")[-1]
            namespace = str(element.tag).split("}")[0]
            taxonomy = (
                "us-gaap"
                if "us-gaap" in namespace
                else "dei"
                if "/dei/" in namespace
                else (element.prefix or "custom")
            )
        start, end, fact_dimensions = contexts[context_id]
        text = _text(element)
        unit_ref = _attr(element, "unitRef")
        number: Decimal | None = None
        try:
            scale = int(_attr(element, "scale") or "0")
        except ValueError:
            issues.append("invalid_numeric_scale")
            continue
        if unit_ref:
            transform = (_attr(element, "format") or "").split(":")[-1].lower()
            supported = {
                "",
                "num-dot-decimal",
                "numcommadot",
                "num-dot-decimal-in",
                "numdash",
                "fixed-zero",
            }
            if transform not in supported:
                issues.append(f"unsupported_numeric_transform:{transform}")
                continue
            cleaned = (
                text.replace(",", "").replace("\u00a0", "").replace(" ", "").replace("\u2212", "-")
            )
            if transform in {"numdash", "fixed-zero"}:
                cleaned = "0"
            if cleaned.startswith("(") and cleaned.endswith(")"):
                cleaned = "-" + cleaned[1:-1]
            if _attr(element, "nil") not in {"true", "1"}:
                try:
                    number = Decimal(cleaned) * Decimal(10) ** scale
                    if _attr(element, "sign") == "-":
                        number = -number
                    if not number.is_finite():
                        raise InvalidOperation
                except InvalidOperation:
                    issues.append("invalid_numeric_value")
                    continue
        facts.append(
            Fact(
                entity_id=entity_id,
                accession=header.accession,
                taxonomy=taxonomy,
                tag=tag,
                context_id=context_id,
                period_start=start,
                period_end=end,
                unit=units.get(unit_ref or ""),
                value_text=text,
                value=number,
                scale=scale,
                decimals=_attr(element, "decimals"),
                dimensions=fact_dimensions,
                filed_date=header.filed_date,
                published_at=header.published_at,
                publication_precision="timestamp" if header.published_at else "date_only",
                raw_sha256=raw_sha256,
                form=header.form,
                document_period_end=document_end,
            )
        )
    if not facts:
        issues.append("no_original_facts_parsed")
    return facts, sorted(set(issues))
