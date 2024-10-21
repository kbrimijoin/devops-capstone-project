"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""

import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL, json=account.serialize(), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL, json=account.serialize(), content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...

    def test_list_all_accounts(self):
        """It should get a list of all Accounts"""
        num_accounts = 7
        self._create_accounts(num_accounts)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), num_accounts)

    def test_get_account_by_id(self):
        """It should return an Account by id"""
        account = self._create_accounts(1)[0].serialize()
        response = self.client.get(BASE_URL + "/" + str(account["id"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], account["id"])

    def test_account_not_found(self):
        """It should return a 404 if the account isn't found"""
        response = self.client.get(BASE_URL + "/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account(self):
        """It should update an existing Account"""
        test_account = AccountFactory()
        response = self.client.post(BASE_URL, json=test_account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_name = "Krissy Brimijoin"
        account = response.get_json()
        account["name"] = new_name

        put_response = self.client.put(
            BASE_URL + "/" + str(account["id"]), json=account
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)

        updated_account = put_response.get_json()
        self.assertEqual(updated_account["name"], new_name)

    def test_update_to_nonexistant_account(self):
        """It should return a 404 if an update to account that doesn't exist is attempted"""
        test_account = AccountFactory().serialize()
        response = self.client.put(BASE_URL + "/0", json=test_account)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account(self):
        """It should delete an existing Account"""
        test_account = AccountFactory().serialize()
        response = self.client.post(BASE_URL, json=test_account)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_account_id = str(response.get_json()["id"])
        delete_response = self.client.delete(BASE_URL + "/" + test_account_id)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        find_response = self.client.get(BASE_URL + "/" + test_account_id)
        self.assertEqual(find_response.status_code, status.HTTP_404_NOT_FOUND)
