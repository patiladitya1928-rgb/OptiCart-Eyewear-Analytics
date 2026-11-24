
from flask import Blueprint, current_app, render_template, request
import pandas as pd

from compare_database import compare_csv_with_database


import_bp = Blueprint("imports", __name__)


@import_bp.route("/import-preview")
def import_preview():

    # Get application resources.
    engine = current_app.extensions["db_engine"]
    reports_dir = current_app.config["REPORTS_DIR"]
    csv_path = current_app.config["CSV_PATH"]
    logger = current_app.logger

    # ----------------------------------------------
    # LOAD LATEST VALIDATION SUMMARY
    # ----------------------------------------------

    summary_files = sorted(
        reports_dir.glob("summary_*.csv"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    summary = {
        "total": 0,
        "valid": 0,
        "rejected": 0,
        "repeated": 0,
        "needs_review": 0
    }

    report_found = False

    if summary_files:

        summary_df = pd.read_csv(summary_files[0])

        counts = dict(
            zip(
                summary_df["status"],
                summary_df["count"]
            )
        )

        summary["total"] = int(
            counts.get("Total rows", 0)
        )

        summary["valid"] = int(
            counts.get("Valid candidates", 0)
        )

        summary["rejected"] = int(
            counts.get("Rejected", 0)
        )

        summary["repeated"] = int(
            counts.get("Repeated IDs", 0)
        )

        summary["needs_review"] = int(
            counts.get("Needs Review", 0)
        )

        report_found = True

    # ----------------------------------------------
    # COMPARE CSV RECORDS WITH DATABASE
    # ----------------------------------------------

    comparison = compare_csv_with_database(
        engine_override=engine
    )

    if comparison is None:

        comparison = {
            "comparison_failed": True,
            "error_message": "Comparison returned no results.",
            "csv_rows": 0,
            "compared_rows": 0,
            "existing_rows": 0,
            "new_records": 0,
            "exact_duplicates": 0,
            "data_conflicts": 0,
            "new_ids": [],
            "exact_duplicate_ids": [],
            "conflict_details": [],
            "repeated_ids": [],
            "repeated_id_count": 0
        }

    else:

        comparison.setdefault(
            "comparison_failed", False
        )

        comparison.setdefault(
            "error_message", None
        )

        comparison.setdefault(
            "compared_rows", 0
        )

        comparison.setdefault(
            "repeated_id_count", 0
        )

        comparison.setdefault(
            "repeated_ids", []
        )

    # ----------------------------------------------
    # PAGINATION SETTINGS
    # ----------------------------------------------

    per_page = 10

    try:
        page = max(
            1,
            int(request.args.get("page", 1))
        )

    except (TypeError, ValueError):
        page = 1

    preview_records = []
    total_records = 0
    total_pages = 0

    # ----------------------------------------------
    # READ CSV RECORDS FOR CURRENT PAGE
    # ----------------------------------------------

    if csv_path.exists():

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            total_records = max(
                sum(1 for _ in file) - 1,
                0
            )

        total_pages = (
            total_records + per_page - 1
        ) // per_page

        page = min(
            page,
            max(total_pages, 1)
        )

        skip_rows = range(
            1,
            (page - 1) * per_page + 1
        )

        preview_df = pd.read_csv(
            csv_path,
            dtype={"order_id": "string"},
            skiprows=skip_rows,
            nrows=per_page
        )

        preview_df.columns = [
            str(column).strip().lower()
            for column in preview_df.columns
        ]

        preview_records = preview_df.to_dict(
            orient="records"
        )

        # ------------------------------------------
        # LOAD LATEST VALIDATION PREVIEW
        # ------------------------------------------

        validation_files = sorted(
            reports_dir.glob("preview_*.csv"),
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        validation_status_by_id = {}

        if validation_files:

            # Scan the report in bounded chunks and retain statuses only
            # for the order IDs visible on this page.
            page_order_ids = {
                str(record.get("order_id", "")).strip()
                for record in preview_records
            }

            try:
                for validation_chunk in pd.read_csv(
                    validation_files[0],
                    dtype="string",
                    usecols=lambda column: str(column).strip().lower()
                    in {"order_id", "preview_status"},
                    chunksize=10000,
                ):
                    validation_chunk.columns = [
                        str(column).strip().lower()
                        for column in validation_chunk.columns
                    ]

                    if not {
                        "order_id",
                        "preview_status"
                    }.issubset(validation_chunk.columns):
                        continue

                    validation_chunk["order_id"] = (
                        validation_chunk["order_id"].str.strip()
                    )

                    matching = validation_chunk[
                        validation_chunk["order_id"].isin(
                            page_order_ids
                        )
                    ]

                    validation_status_by_id.update(
                        dict(
                            zip(
                                matching["order_id"],
                                matching["preview_status"].str.strip()
                            )
                        )
                    )

                    if page_order_ids.issubset(
                        validation_status_by_id
                    ):
                        break

            except (ValueError, pd.errors.EmptyDataError):
                logger.warning(
                    "Validation preview report could not be read",
                    exc_info=True
                )

        # ------------------------------------------
        # DATABASE STATUS LOOKUP
        # ------------------------------------------

        exact_duplicate_ids = {
            str(order_id).strip()
            for order_id in comparison.get(
                "exact_duplicate_ids", []
            )
        }

        conflict_ids = {
            str(item["order_id"]).strip()
            for item in comparison.get(
                "conflict_details", []
            )
        }

        # ------------------------------------------
        # ATTACH STATUS TO EACH PREVIEW RECORD
        # ------------------------------------------

        for record in preview_records:

            order_id = str(
                record.get("order_id", "")
            ).strip()

            status = validation_status_by_id.get(
                order_id,
                "Not found"
            )

            if status == "Valid candidate":

                if order_id in conflict_ids:
                    status = "Data conflict"

                elif order_id in exact_duplicate_ids:
                    status = "Exact existing duplicate"

            record["preview_status"] = status

    # ----------------------------------------------
    # RENDER IMPORT PREVIEW PAGE
    # ----------------------------------------------

    return render_template(
        "import_preview.html",
        summary=summary,
        report_found=report_found,
        comparison=comparison,
        preview_records=preview_records,
        page=page,
        total_pages=total_pages,
        total_records=total_records
    )
