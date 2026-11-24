
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

CSV_PATH = BASE_DIR / "dataset/processed/Lenskart_India_processed.csv"
REPORTS_DIR = BASE_DIR / "reports"

MANIFEST_PATH = REPORTS_DIR / "validation_manifest.json"


def calculate_sha256(file_path):
    """Calculate the SHA-256 fingerprint of a file."""

    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_manifest():

    if not CSV_PATH.exists():
        raise FileNotFoundError("Processed CSV not found.")

    preview_files = sorted(
        REPORTS_DIR.glob("preview_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    if not preview_files:
        raise FileNotFoundError("Validation preview report not found.")

    preview_path = preview_files[0]

    print("Verifying validation report...")

    csv_df = pd.read_csv(
        CSV_PATH,
        dtype={"order_id": "string"}
    )

    preview_df = pd.read_csv(
        preview_path,
        dtype={"order_id": "string"}
    )

    csv_df.columns = csv_df.columns.str.strip().str.lower()
    preview_df.columns = preview_df.columns.str.strip().str.lower()

    if not set(csv_df.columns).issubset(set(preview_df.columns)):
        raise ValueError("Validation report columns do not match CSV.")

    preview_data = preview_df[csv_df.columns].copy()

    if len(csv_df) != len(preview_data):
        raise ValueError("CSV and preview row counts do not match.")

    if not csv_df.fillna("").astype(str).equals(
        preview_data.fillna("").astype(str)
    ):
        raise ValueError("CSV and validation preview contents differ.")

    if "preview_status" not in preview_df.columns:
        raise ValueError("Validation status column is missing.")

    if not preview_df["preview_status"].eq("Valid candidate").all():
        raise ValueError("Not all records are valid candidates.")

    print("Validation report matches the processed CSV.")

    manifest = {
        "csv_file": CSV_PATH.name,
        "csv_sha256": calculate_sha256(CSV_PATH),
        "preview_file": preview_path.name,
        "preview_sha256": calculate_sha256(preview_path),
        "total_rows": len(csv_df),
        "valid_candidates": int(
            preview_df["preview_status"].eq("Valid candidate").sum()
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat()
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    print("\n========== MANIFEST CREATED ==========")
    print("CSV SHA-256:", manifest["csv_sha256"])
    print("Preview SHA-256:", manifest["preview_sha256"])
    print("Total rows:", manifest["total_rows"])
    print("Valid candidates:", manifest["valid_candidates"])
    print("Manifest file:", MANIFEST_PATH.name)

    print("\nNo database records were modified.")


if __name__ == "__main__":
    create_manifest()

