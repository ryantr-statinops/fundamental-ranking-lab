"""Pack raw SEC data into a lightweight bundle for Google Colab/Cloud execution.

Filters out giant full-text submission files (<SEC-DOCUMENT> .txt) while preserving:
- All XBRL/XML filing documents (balance sheets, income statements, cash flows)
- All metadata JSON files (submissions, facts, index)
- The persistent index cache (.records_cache.json)
"""
import json
import pathlib
import sys
import time
import zipfile

def pack_bundle(data_dir: pathlib.Path, output_zip: pathlib.Path) -> None:
    raw_dir = data_dir / "raw"
    cache_file = raw_dir / ".records_cache.json"
    if not raw_dir.exists() or not cache_file.exists():
        print(f"Error: {raw_dir} or {cache_file} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading cache index from {cache_file}...")
    start_time = time.time()
    cache_data = json.loads(cache_file.read_text(encoding="utf-8"))

    # Identify filing_text files to truncate to 64KB
    filing_texts: set[str] = set()
    for item in cache_data.values():
        if item.get("kind") == "filing_text":
            rel = item.get("relative_path")
            if rel:
                filing_texts.add(rel.replace("\\", "/"))

    all_files = [p for p in (raw_dir / "sec").rglob("*") if p.is_file()]
    print(f"Total files in sec directory: {len(all_files):,}")
    print(f"Filing text headers to compress efficiently: {len(filing_texts):,}")
    print(f"Writing optimized bundle to {output_zip} ...")

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
        # 1. Write the cache index
        zf.write(cache_file, ".records_cache.json")

        # 2. Write all files
        saved_bytes = 0
        for i, p in enumerate(all_files, 1):
            rel_str = p.relative_to(raw_dir).as_posix()
            if rel_str in filing_texts:
                # Store only the first 64KB for filing_text headers
                content = p.read_bytes()[: 64 * 1024]
                saved_bytes += max(0, p.stat().st_size - len(content))
                zf.writestr(rel_str, content)
            else:
                zf.write(p, rel_str)

            if i % 3000 == 0 or i == len(all_files):
                print(f"Packed {i:,} / {len(all_files):,} files...")

    elapsed = round(time.time() - start_time, 1)
    saved_gb = round(saved_bytes / (1024**3), 2)
    bundle_size_gb = round(output_zip.stat().st_size / (1024**3), 2)
    print(f"Skipped {saved_gb} GB of redundant text data!")
    print(f"SUCCESS! Created optimized bundle {output_zip} ({bundle_size_gb} GB) in {elapsed}s.")


if __name__ == "__main__":
    base = pathlib.Path(__file__).resolve().parents[1]
    pack_bundle(base / "data", base / "pilot_raw_bundle.zip")
