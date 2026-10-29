"""Export audited historical universe Parquet tables for downstream ranking and datasets."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys


def export_universe(input_run_dir: pathlib.Path, output_dir: pathlib.Path) -> None:
    if not input_run_dir.exists():
        print(f"Error: input run directory {input_run_dir} does not exist.", file=sys.stderr)
        sys.exit(1)

    parquets = list(input_run_dir.glob("*.parquet"))
    if not parquets:
        print(f"Error: no Parquet tables found in {input_run_dir}.", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Exporting {len(parquets)} universe tables from {input_run_dir} to {output_dir}...")

    for p in parquets:
        dest = output_dir / p.name
        shutil.copy2(p, dest)
        size_kb = round(dest.stat().st_size / 1024, 2)
        print(f"  + {p.name:<30} ({size_kb} KB)")

    print(f"\nSUCCESS! Exported universe tables to {output_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export audited universe Parquet tables")
    parser.add_argument("--input-run", required=True, help="Path to audited universe run directory")
    parser.add_argument(
        "--output-dir",
        default="data/universe",
        help="Target export directory (default: data/universe)",
    )
    args = parser.parse_args()

    export_universe(pathlib.Path(args.input_run), pathlib.Path(args.output_dir))
