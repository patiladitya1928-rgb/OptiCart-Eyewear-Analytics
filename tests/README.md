# OptiCart test suite

Run the unit and route tests from the project root:

```bash
python -m pytest -q
```

The normal suite uses an in-memory SQLite URL only to allow Flask application setup; it does not create tables or change the project database. Route tests mock database failures where required.

The live database smoke test is skipped by default. To opt in after configuring `DATABASE_URL` for the intended MySQL database:

```bash
RUN_DB_INTEGRATION=1 python -m pytest -q tests/test_db.py
```

Do not run the integration test against a production database unless a read-only connection is intended.
