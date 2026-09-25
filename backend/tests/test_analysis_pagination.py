from datetime import date, datetime, time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.analyses import _list_query
from app.core.database import Base
from app.models import AnalysisSession, Location, Project, User


def test_analysis_pages_are_stable_and_respect_ownership():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([User(id=1, username='owner', password_hash='test'), User(id=2, username='other', password_hash='test')])
        db.add_all([Project(id=1, name='Owned', owner_id=1), Project(id=2, name='Private', owner_id=2)])
        db.add_all([Location(id=1, project_id=1, name='Owned'), Location(id=2, project_id=2, name='Private')])
        for index in range(1, 5):
            db.add(AnalysisSession(id=index, location_id=1 if index < 4 else 2,
                analysis_date=date(2026, 9, 24), start_time=time(7), end_time=time(8),
                created_at=datetime(2026, 9, 24)))
        db.commit()
        def ids(offset, project=None, location=None):
            return [row.id for row in db.scalars(_list_query(1, project, location, 2, offset)).unique()]
        assert ids(0) == [3, 2]
        assert ids(2) == [1]
        assert ids(4) == []
        assert ids(0, project=2) == []
        assert ids(0, location=2) == []
    engine.dispose()
