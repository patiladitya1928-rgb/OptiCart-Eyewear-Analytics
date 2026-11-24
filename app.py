# Standard library
import logging
from datetime import date
from pathlib import Path

# Third-party libraries
from flask import Flask, render_template
from sqlalchemy.exc import SQLAlchemyError

# Project modules
from config import Config
from extensions import create_db_engine
from analytics import calculate_average_order_value

# Blueprints
from routes.dashboard_routes import dashboard_bp
from routes.import_routes import import_bp
from routes.sales_routes import sales_bp


# --------------------------------------------------
# FLASK APPLICATION
# --------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

CSV_PATH = (
    BASE_DIR
    / "dataset"
    / "processed"
    / "Lenskart_India_processed.csv"
)

app.config["REPORTS_DIR"] = REPORTS_DIR
app.config["CSV_PATH"] = CSV_PATH

logger = logging.getLogger(__name__)


# --------------------------------------------------
# DATE VALIDATION
# --------------------------------------------------

def validate_sales_date_range(start_date, end_date):
    """Validate optional ISO dates and ensure the start is not after the end."""

    parsed_start = date.fromisoformat(start_date) if start_date else None
    parsed_end = date.fromisoformat(end_date) if end_date else None

    if parsed_start and parsed_end and parsed_start > parsed_end:
        raise ValueError("Start date cannot be after the end date.")

    return parsed_start, parsed_end


app.extensions["validate_sales_date_range"] = validate_sales_date_range


# --------------------------------------------------
# DATABASE ERROR HANDLING
# --------------------------------------------------

@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    """Show a safe, user-friendly response for database failures."""

    logger.error(
        "Database operation failed",
        exc_info=(type(error), error, error.__traceback__),
    )

    return render_template(
        "error.html",
        message="The dashboard could not retrieve data right now. Please try again shortly.",
    ), 503


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

engine = create_db_engine()

app.extensions["db_engine"] = engine


# --------------------------------------------------
# BLUEPRINT REGISTRATION
# --------------------------------------------------

app.register_blueprint(dashboard_bp)
app.register_blueprint(import_bp)
app.register_blueprint(sales_bp)


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
