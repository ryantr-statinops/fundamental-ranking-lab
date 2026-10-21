"""Pack raw SEC data into a lightweight bundle for Google Colab/Cloud execution.

Filters out giant full-text submission files (<SEC-DOCUMENT> .txt) while preserving:
- All XBRL/XML filing documents (balance sheets, income statements, cash flows)
- All metadata JSON files (submissions, facts, index)
- The persistent index cache (.records_cache.json)
"""

import pathlib
import sys
import time
import zipfile


def pack_bundle(data_dir: pathlib.Path, output_zip: pathlib.Path) -> None:
    raw_dir = data_dir / "raw"
    if not raw_dir.exists():
        print(f"Error: {raw_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning files in {raw_dir}...")
    start_time = time.time()
    
    files_to_pack: list[pathlib.Path] = []
    skipped_txt_count = 0
    skipped_txt_bytes = 0

    cache_file = raw_dir / ".records_cache.json"
    if cache_file.exists():
        files_to_pack.append(cache_file)

    for p in (raw_dir / "sec").rglob("*"):
        if not p.is_file():
            continue
        # Check if it's a huge SEC-DOCUMENT text file
        s = p.stat().st_size
        if s > 1024 * 1024:
            try:
                is_txt = (
                    b"<SEC-DOCUMENT>" in head
                    or b"<DOCUMENT>" in head
                    or b"-----BEGIN PRIVACY" in head
                )
                if is_txt:
                    skipped_txt_count += 1
                    skipped_txt_bytes += s
                    continue
            except Exception:
                pass
        files_to_pack.append(p)

    print(f"Selected {len(files_to_pack):,} files for packing.")
    saved_gb = round(skipped_txt_bytes / (1024**3), 2)
    print(f"Skipped {skipped_txt_count:,} text files ({saved_gb} GB saved).")
    print(f"Writing compressed bundle to {output_zip} ...")
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=5) as zf:
        for i, f in enumerate(files_to_pack, 1):
            arcname = f.relative_to(raw_dir)
            zf.write(f, arcname)
            if i % 2000 == 0 or i == len(files_to_pack):
                print(f"Packed {i:,} / {len(files_to_pack):,} files...")

    elapsed = round(time.time() - start_time, 1)
    bundle_size_gb = round(output_zip.stat().st_size / (1024**3), 2)
    print(f"SUCCESS! Created bundle {output_zip} ({bundle_size_gb} GB) in {elapsed}s.")


if __name__ == "__main__":
    base = pathlib.Path(__file__).resolve().parents[1]
    pack_bundle(base / "data", base / "pilot_raw_bundle.zip")
