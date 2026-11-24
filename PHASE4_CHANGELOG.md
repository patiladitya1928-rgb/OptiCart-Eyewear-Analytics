# OptiCart — Phase 4 delivery notes

## Phase 4.1 — Reliability and testing
- Kept safe SQLAlchemy database error handling in the Flask app.
- Added/retained unit coverage for KPI calculations, date validation, chart empty states and chart rendering.
- Added pure helper tests for period comparisons, percentage changes, revenue contribution and SQL filter construction.
- Added a requirements manifest so the project dependencies can be installed consistently.
- Kept the live MySQL smoke test opt-in.

## Phase 4.2 — Database performance
- Sales filters now add only predicates that are actually selected, rather than using nullable OR conditions for every field.
- CSV-to-MySQL comparison fetches only matching incoming order IDs in batches of 500 instead of loading every row from the sales table into Python memory.
- The Flask import-preview route reuses the application's SQLAlchemy engine for comparison instead of creating and disposing a second engine on every request.
- Validation preview statuses are scanned in bounded chunks and only statuses for the currently visible page are retained.
- No database schema or index changes were made. Production index choices should be based on EXPLAIN plans and actual MySQL workload.

## Phase 4.3 — Maintainability
- Added `services/metrics.py` for pure reporting calculations.
- Added `repositories/sales_repository.py` for reusable parameterized sales-filter construction.
- Added package structure for `services/` and `repositories/` without changing the existing Flask route URLs.
- Preserved existing route entry points and business formula.

## Phase 4.4 — KPI enhancement
- Sales analytics now compares a selected complete date range with the immediately preceding period of equal inclusive length.
- Revenue and order percentage changes are shown with explicit comparison dates.
- A zero prior-period baseline is treated as undefined/new activity instead of dividing by zero.
- No comparison is shown for incomplete date ranges or when no explicit date range is selected.

## Phase 4.5 — Sales analytics and filters
- Active date, state and city selections are reflected in the reporting context.
- Top product category and top sales channel are surfaced with their share of filtered revenue.
- Filter predicates remain parameterized.
- Existing state/city option validation remains in place.

## Phase 4.6 — Plotly, responsive UI and final QA
- Added responsive insight-card styling with a single-column mobile layout.
- Added visible keyboard focus treatment for filter controls.
- Preserved Plotly chart builders and existing chart IDs.
- Corrected demographic chart labels to say sales records, not customers. The dataset does not contain a customer identifier, so these charts cannot count unique customers.

## Preserved constraints
- Flask, MySQL, Pandas, SQLAlchemy and Plotly remain the application stack.
- The revenue calculation remains `quantity * unit_price * (100 - discount_percent) / 100.0`.
- No machine learning, schema migration, or fabricated customer-level metrics were introduced.

## Verification performed in the build environment
- Python compilation: passed.
- Jinja template parsing: passed for all four templates.
- Focused helper and Plotly tests: 19 passed.
- Full pytest collection: blocked because Flask is not installed in the build environment (`ModuleNotFoundError: No module named 'flask'`).
- Live MySQL query plans, real database comparison, and interactive browser/mobile rendering were not executed in this environment.

Install dependencies in the project's virtual environment with `python -m pip install -r requirements.txt`, then run `python -m pytest -q` and launch the app against the configured MySQL database for environment-specific integration checks.
