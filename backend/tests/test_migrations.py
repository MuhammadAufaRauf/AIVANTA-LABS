from sqlalchemy import create_engine, inspect, text

from app.db.migrations import migrate_legacy_tables


def test_legacy_company_config_migration_is_additive_and_idempotent():
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE company_config (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO company_config (id) VALUES (1)"))
    migrate_legacy_tables(engine)
    migrate_legacy_tables(engine)
    columns = {column["name"] for column in inspect(engine).get_columns("company_config")}
    assert {"id", "company_name", "product_name", "business_model"}.issubset(columns)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM company_config")) == 1
    engine.dispose()
