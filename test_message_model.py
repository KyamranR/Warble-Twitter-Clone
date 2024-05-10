"""Testing Message Model"""


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

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

            db.session.commit()

            user1 = User.query.get(user_id1)
            
            self.user1 = user1
            self.user_id1 = user_id1

            self.client = app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            res = super().tearDown()
            db.session.rollback()
            return res
        

    def test_message_model(self):
        """Testing message model"""
        with app.app_context():
            
            message = Message(text='new message', user_id=self.user1.id)

            db.session.add(message)
            db.session.commit()

            self.user1 = User.query.get(self.user_id1)

            self.assertEqual(len(self.user1.messages), 1)
            self.assertEqual(self.user1.messages[0].text, 'new message')

    def test_message_likes(self):
        """Testing if user can like other user message"""
        with app.app_context():
            message1 = Message(text='message1', user_id=self.user_id1)

            message2 = Message(text='message2', user_id=self.user_id1)

            user = User.signup('newuser', 'test@test.com', 'password', None)
            user_id = 123
            user.id = user_id

            db.session.add_all([message1, message2, user])
            db.session.commit()

            user.likes.append(message1)

            db.session.commit()

            like = Likes.query.filter(Likes.user_id == user_id).all()

            self.assertEqual(len(like), 1)
            self.assertEqual(like[0].message_id, message1.id)