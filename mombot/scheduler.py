from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.util import undefined
from apscheduler.job import Job

from discord.ext import commands
import datetime as dt

# Annotation imports
from typing import (
    Optional,
    List,
    Sequence
)

class Scheduler(AsyncIOScheduler):

    def __init__(self, mysql_creds: str) -> None:
        url = f"mariadb+pymysql://{mysql_creds}/flask?charset=utf8mb4"
        self.js = {'default': SQLAlchemyJobStore(url=url)}
        super().__init__(jobstores=self.js)

    def get_user_jobs(self, user: int, string: bool = False
                      ) -> Optional[Sequence[Job]]:
        jobs = self.get_jobs()
        user_jobs = []
        for job in jobs:
            if user == job.kwargs["user"]:
                if string:
                    user_jobs.append(str(job))
                else:
                    user_jobs.append(job)
        return user_jobs
