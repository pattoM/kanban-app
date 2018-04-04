#run with: python -m unittest -v
#delete the db on subsequent runs or make entirely new names for the register function

import os
import unittest
from app import *
from flask import url_for

TEST_DB = "test1.db"

class BasicAppTests(unittest.TestCase):
    #set up a mock db
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG']=False
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test1.db'
        self.app = app.test_client()
        db.create_all()

    def teardown(self):
        pass

    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def register_ts(self, email, username, password):
        return self.app.post('/signup', data=dict(email=email, username=username, password=password, follow_redirects=True))

    def login_ts(self, username, password):
        return self.app.post('/login', data=dict(username=username,password=password), follow_redirects=True)
    def test_user_reg(self):
        response=self.register_ts('test@test.com','test','123456789')
        self.assertEqual(response.status_code, 302) #because a redirect is expected

    def clear_db(self):
        db.drop_all()

if __name__=="__main__":
    unittest.main()
