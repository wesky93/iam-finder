from datetime import datetime
from typing import List

import arrow
import boto3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AccessKey(BaseModel):
    id: str
    created_at: datetime


class User(BaseModel):
    arn: str
    name: str
    created_at: datetime
    access_keys: List[AccessKey]


class Statistics(BaseModel):
    total_user_count: int
    total_access_key_count: int


class IAMUserSearchResult(BaseModel):
    results: List[User]
    statistics: Statistics


@app.get("/iam/users/search/by_access_key_age", response_model=IAMUserSearchResult)
def iam_search(access_key_age: int):
    iam = boto3.resource('iam')

    total_user_count = 0
    total_access_key_count = 0

    now = arrow.now('UTC')
    created_at_before = now.shift(hours=-access_key_age).datetime

    results = []

    for user in iam.users.all():
        access_keys = [
            key for key in user.access_keys.all()
            if key.create_date <= created_at_before and key.status == 'Active'
        ]

        if access_keys:
            total_user_count += 1
            total_access_key_count += len(access_keys)

            _access_keys = [AccessKey(id=k.id, created_at=k.create_date) for k in access_keys]
            user = User(
                arn=user.arn,
                name=user.user_name,
                created_at=user.create_date,
                access_keys=_access_keys
            )
            results.append(user)

    stat = Statistics(
        total_user_count=total_user_count,
        total_access_key_count=total_access_key_count
    )

    return IAMUserSearchResult(
        results=results,
        statistics=stat,
    )
