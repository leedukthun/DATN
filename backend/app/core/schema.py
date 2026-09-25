from __future__ import annotations

from sqlalchemy import inspect, text

from app.core.database import Base, engine


def ensure_schema() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "projects" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("projects")}
    if "owner_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE projects ADD COLUMN owner_id INTEGER"))
    
    # Add hourly_violations_json column to analysis_sessions if it doesn't exist
    if "analysis_sessions" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("analysis_sessions")}
        if "hourly_violations_json" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE analysis_sessions ADD COLUMN hourly_violations_json TEXT"))
