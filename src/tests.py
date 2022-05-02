import unittest
import uuid

import boto3
import arrow
from freezegun import freeze_time
from moto import mock_iam
from fastapi.testclient import TestClient

from main import app


def creat_user(name: str = None):
    name = name or uuid.uuid4().hex[:6]
    iam = boto3.resource('iam')
    user = iam.User(name).create()
    return user


def creat_access_key(user, access_key_age: int = 0, active=True):
    """
    특정 수명을 가진 액세스키를 생성
    :param user:
    :param access_key_age:
    :return:
    """

    created_at = arrow.now('UTC').shift(hours=-access_key_age).datetime
    with freeze_time(created_at):
        access_key = user.create_access_key_pair()
        if not active:
            access_key.deactivate()
    return access_key


class MockIAMTestCase(unittest.TestCase):

    def setUp(self):
        self.mock = mock_iam()
        self.mock.start()

        self.client = TestClient(app)
        self.url = "/iam/users/search/by_access_key_age"

    def test_empty_list(self):
        user1 = creat_user()
        creat_access_key(user1, access_key_age=10)

        user2 = creat_user()
        creat_access_key(user2, access_key_age=19)
        creat_access_key(user2, access_key_age=50)

        user3 = creat_user()
        creat_access_key(user3, access_key_age=1)
        creat_access_key(user3, access_key_age=800)

        resp = self.client.get(self.url, params={"access_key_age": 9000})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        stat = body["statistics"]
        self.assertEqual(stat['total_user_count'], 0)
        self.assertEqual(stat['total_access_key_count'], 0)

        results = body["results"]
        self.assertEqual(len(results), 0)

    def test_old_access_key(self):
        # 오래된 키를 가진 사용자
        user1 = creat_user()
        user1_access_key = creat_access_key(user1, access_key_age=100)

        # 오래된 키를 2개 가진 사용자
        user2 = creat_user()
        user_2_access_keys = [
            creat_access_key(user2, access_key_age=100),
            creat_access_key(user2, access_key_age=400),
        ]

        # 최신키를 가진 사용자
        user3 = creat_user()
        creat_access_key(user3, access_key_age=13)

        # 최신키, 오래된 키를 가진 사용자
        user4 = creat_user()
        creat_access_key(user4, access_key_age=10)
        user4_access_key = creat_access_key(user4, access_key_age=340)

        resp = self.client.get(self.url, params={"access_key_age": 90})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        stat = body["statistics"]
        self.assertEqual(stat['total_user_count'], 3)
        self.assertEqual(stat['total_access_key_count'], 4)

        results = body["results"]
        self.assertEqual(len(results), stat['total_user_count'])

        excepted_user_names = set([user1.name, user2.name, user4.name])
        self.assertEqual(excepted_user_names, set([r['name'] for r in results]))

        with self.subTest('오래된 키를 가진 사용자 테스트'):
            result_user_1 = [i for i in results if i['arn'] == user1.arn][0]
            self.assertEqual(len(result_user_1['access_keys']), 1)
            self.assertEqual(
                user1_access_key.access_key_id,
                result_user_1['access_keys'][0]['id']
            )

        with self.subTest('오래된 키를 2개 가진 사용자 테스트'):
            result_user_2 = [i for i in results if i['arn'] == user2.arn][0]
            self.assertEqual(len(result_user_2['access_keys']), 2)
            self.assertEqual(
                set([k.access_key_id for k in user_2_access_keys]),
                set([k['id'] for k in result_user_2['access_keys']])
            )

        with self.subTest('최신키, 오래된 키를 가진 사용자 테스트'):
            result_user_4 = [i for i in results if i['arn'] == user4.arn][0]
            self.assertEqual(len(result_user_4['access_keys']), 1)
            self.assertEqual(
                user4_access_key.access_key_id,
                result_user_4['access_keys'][0]['id']
            )

    def test_inactive_access_key(self):
        # 오래된 키, 유효하지 않은 오래된 키를 가진 사용자
        user1 = creat_user()
        user1_access_key = creat_access_key(user1, access_key_age=100)
        creat_access_key(user1, access_key_age=100, active=False)

        # 최신키, 유효하지 않은 최신 키를 가진 사용자
        user2 = creat_user()
        creat_access_key(user2, access_key_age=1)
        creat_access_key(user2, access_key_age=10, active=False)

        # 최신키, 오래된 키를 가진 사용자
        user3 = creat_user()
        creat_access_key(user3, access_key_age=10)
        user3_access_key = creat_access_key(user3, access_key_age=400)

        resp = self.client.get(self.url, params={"access_key_age": 90})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()

        stat = body["statistics"]
        self.assertEqual(stat['total_user_count'], 2)
        self.assertEqual(stat['total_access_key_count'], 2)

        results = body["results"]
        self.assertEqual(len(results), stat['total_user_count'])

        with self.subTest('유효하지 않은 오래된 키를 가진 사용자 테스트'):
            data = [i for i in results if i['arn'] == user1.arn]
            self.assertTrue(data)

            result_user_1 = data[0]
            self.assertEqual(result_user_1['name'], user1.user_name)
            self.assertEqual(len(result_user_1['access_keys']), 1)

            self.assertEqual(result_user_1['access_keys'][0]['id'], user1_access_key.access_key_id)

    def tearDown(self):
        self.mock.stop()
