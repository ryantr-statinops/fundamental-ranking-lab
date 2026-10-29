"""Upload cleaned point-in-time financial dataset to Hugging Face Hub."""

from __future__ import annotations

import argparse
import os
import pathlib
import sys


def upload_dataset(repo_id: str, token: str | None = None) -> None:
    data_dir = pathlib.Path(__file__).resolve().parents[1] / "data" / "huggingface"
    if not data_dir.exists():
        print(f"Error: {data_dir} does not exist. Run export first.", file=sys.stderr)
        sys.exit(1)

    hf_token = token or os.environ.get("HF_TOKEN")
    if not hf_token:
        print("Error: Hugging Face token is required.", file=sys.stderr)
        print("Set HF_TOKEN environment variable or pass --token <your_token>", file=sys.stderr)
        sys.exit(1)

    try:
        from huggingface_hub import HfApi  # type: ignore[import-untyped]
    except ImportError:
        print("Installing huggingface_hub...", flush=True)
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"])
        from huggingface_hub import HfApi

    api = HfApi(token=hf_token)

    print(f"Ensuring dataset repository exists: {repo_id}...")
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)

    print(f"Uploading files from {data_dir} to Hugging Face dataset '{repo_id}'...")
    api.upload_folder(
        folder_path=str(data_dir),
        repo_id=repo_id,
        repo_type="dataset",
    )
    print(f"\nSUCCESS! Dataset is live at: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset to Hugging Face")
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Hugging Face repo id, e.g. 'username/us-equities-sec-fundamentals'",
    )
    parser.add_argument("--token", help="Hugging Face User Access Token (write permission)")
    args = parser.parse_args()

    upload_dataset(args.repo_id, args.token)
