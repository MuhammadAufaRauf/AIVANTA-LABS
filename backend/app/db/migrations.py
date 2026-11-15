from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def migrate_legacy_tables(engine: Engine) -> None:
    """Additive compatibility migration for the original Phase 1 SQLite table."""
    inspector = inspect(engine)
    if "company_config" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("company_config")}
    additions = {
        "company_name": "VARCHAR(120) NOT NULL DEFAULT 'Aivanta Labs'",
        "product_name": "VARCHAR(120) NOT NULL DEFAULT 'Aivanta OS'",
        "tagline": "VARCHAR(200) NOT NULL DEFAULT 'Intelligence. Innovation. Automation.'",
        "industry": "VARCHAR(120) NOT NULL DEFAULT 'Artificial Intelligence & Technology'",
        "market": "VARCHAR(80) NOT NULL DEFAULT 'Global'",
        "founder_role": "VARCHAR(80) NOT NULL DEFAULT 'Founder & CEO'",
        "business_model": "VARCHAR(160) NOT NULL DEFAULT 'AI & Software Agency + Digital Products'",
    }
    with engine.begin() as connection:
        for column_name, definition in additions.items():
            if column_name not in columns:
                connection.execute(text(f"ALTER TABLE company_config ADD COLUMN {column_name} {definition}"))
