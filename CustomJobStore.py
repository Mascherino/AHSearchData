from __future__ import absolute_import

from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import maybe_ref, datetime_to_utc_timestamp

try:
    from sqlalchemy import (
        create_engine, Table, Column, MetaData, Unicode,
        Float, LargeBinary, select, and_, VARCHAR)
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.expression import null
except ImportError:  # pragma: nocover
    raise ImportError('SQLAlchemyJobStore requires SQLAlchemy installed')

import pickle

class CustomJobStore(SQLAlchemyJobStore):

    def __init__(self, url=None, engine=None, tablename='apscheduler_jobs',
                 metadata=None, pickle_protocol=pickle.HIGHEST_PROTOCOL,
                 tableschema=None, engine_options=None):
        self.pickle_protocol = pickle_protocol
        metadata = maybe_ref(metadata) or MetaData()

        if engine:
            self.engine = maybe_ref(engine)
        elif url:
            self.engine = create_engine(url, **(engine_options or {}))
        else:
            raise ValueError('Need either "engine" or "url" defined')

        # 191 = max key length in MySQL for InnoDB/utf8mb4 tables,
        # 25 = precision that translates to an 8-byte float
        self.jobs_t = Table(
            tablename, metadata,
            Column('id', Unicode(191, _warn_on_bytestring=False),
                   primary_key=True),
            Column('next_run_time', Float(25), index=True),
            Column('job_state', LargeBinary, nullable=False),
            Column('user', VARCHAR(255)),
            schema=tableschema
        )

    def add_job(self, job):
        insert = self.jobs_t.insert().values(**{
            'id': job.id,
            'next_run_time': datetime_to_utc_timestamp(job.next_run_time),
            'job_state': pickle.dumps(job.__getstate__(), self.pickle_protocol),
            'user': job.user
        })
        try:
            self.engine.execute(insert)
        except IntegrityError:
            raise ConflictingIdError(job.id)
