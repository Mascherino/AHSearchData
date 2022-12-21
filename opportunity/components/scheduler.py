from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.job import Job

import tzlocal

# Annotation imports
from typing import (
    Optional,
    List
)

class Scheduler(AsyncIOScheduler):

    def __init__(self, mysql_creds: str) -> None:
        url = f"mariadb+pymysql://{mysql_creds}/flask?charset=utf8mb4"
        self.js = {
            'default': SQLAlchemyJobStore(
                url=url,
                engine_options={"pool_pre_ping": True, "pool_recycle": 300}),
            'memory': MemoryJobStore()}
        super().__init__(
            jobstores=self.js,
            timezone=str(tzlocal.get_localzone()))

    def get_user_jobs(self, user: int, string: bool = False
                      ) -> Optional[List[Job]]:
        jobs = self.get_jobs('default')
        user_jobs = []
        for job in jobs:
            if user == job.kwargs["user"]:
                if string:
                    user_jobs.append(str(job))
                else:
                    user_jobs.append(job)
        return user_jobs
