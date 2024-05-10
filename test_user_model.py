"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            user1 = User.signup("user1", "user1@test.com", "password", None)
            user_id1 = 1111
            user1.id = user_id1

            user2 = User.signup("user2", "user2@test.com", "password", None)
            user_id2 = 2222
            user2.id = user_id2

            db.session.commit()

            user1 = User.query.get(user_id1)
            user2 = User.query.get(user_id2)

            self.user1 = user1
            self.user_id1 = user_id1

            self.user2 = user2
            self.user_id2 = user_id2

            self.client = app.test_client()
        

    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res
        

    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
            )

            db.session.add(user)
            db.session.commit()

            # User should have no messages & no followers
            self.assertEqual(len(user.messages), 0)
            self.assertEqual(len(user.followers), 0)

    # Testing repr method
    def test_repr(self):
        """Testing the repr method"""

        with app.app_context():
            user = User(email='user@test.com', username='testuser')

            self.assertEqual(repr(user), f'<User #{user.id}: {user.username}, {user.email}>')

    # Testing follow methods
    def test_is_following(self):
        """Checking if user1 is following user 2"""
        with app.app_context():
            user1 = self.user1
            user2 = self.user2

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            user1.following.append(user2)

            self.assertTrue(user1.is_following(user2))
            
            user1.following.remove(user2)
            self.assertFalse(user1.is_following(user2))


    def test_is_followed_by(self):
        """Checking if user1 is followed by user2"""
        with app.app_context():
            user1 = self.user1
            user2 = self.user2

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            user1.following.append(user2)

            self.assertTrue(user2.is_followed_by(user1))
            self.assertFalse(user1.is_followed_by(user2))

    # Testing signup methods
    def test_signup(self):
        """Testing create new user with valid credentials"""
        with app.app_context():
            new_user = User.signup("testtesttest", "testtest@test.com", "password", None)
            user_id = 1
            new_user.id = user_id
            db.session.commit()

            new_user = User.query.get(user_id)
            self.assertIsNotNone(new_user)
            self.assertEqual(new_user.username, "testtesttest")
            self.assertEqual(new_user.email, "testtest@test.com")
            self.assertNotEqual(new_user.password, "password")
            self.assertTrue(new_user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Checking if given invalid username will it fail"""
        with app.app_context():
        
            with self.assertRaises(exc.IntegrityError) as context:
                User.signup(None, 'user@test.com', 'password', None)
                db.session.commit()

    def test_invalid_email_signup(self):
        """Checking if given invalid email will it fail"""
        with app.app_context():
            with self.assertRaises(exc.IntegrityError) as context:
                User.signup('user', None, 'password', None)
                db.session.commit()

    def test_invalid_password_signup(self):
        """Checking if given invalid password will it fail"""
        with app.app_context():
            with self.assertRaises(ValueError) as context:
                User.signup('user', 'test@test.com', None, None)

    #Testing authentication methods
    def test_valid_authentication(self):
        """Checking if successfully return a user when given a valid username and password"""
        with app.app_context():
            user = User.authenticate(self.user1.username, 'password')
            
            self.assertIsNotNone(user)
            self.assertEqual(user.id, self.user_id1)

    def test_invalid_username(self):
        with app.app_context():
            self.assertFalse(User.authenticate('invaliduser', 'password'))

    def test_wrong_password(self):
        with app.app_context():
            self.assertFalse(User.authenticate('user1', 'wrongpassword'))


if __name__ == '__main__':
    import unittest
    unittest.main()

