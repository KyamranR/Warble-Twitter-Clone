import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    db.create_all()

class MessageViewTestCase(TestCase):
    """Test user views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.client = app.test_client()

            self.testuser = User.signup(username="testuser",
                                        email="test@test.com",
                                        password="password",
                                        image_url=None)
            self.testuser_id = 1212
            self.testuser.id = self.testuser_id

            self.user1 = User.signup("user1", "user1@test.com", "password", None)
            self.user1_id = 111
            self.user1.id = self.user1_id

            self.user2 = User.signup("user2", "user2@test.com", "password", None)
            self.user2_id = 222
            self.user2.id = self.user2_id

            self.user3 = User.signup("user3", "user3@test.com", "password", None)
            self.user3_id = 333
            self.user3.id = self.user3_id

            db.session.commit()

            msg1 = Message(
                id=1111,
                text='test message 1',
                user_id=self.testuser.id
            )

            db.session.add(msg1)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.rollback()
        return super().tearDown()

    def test_users(self):
        """Testing users"""
        with self.client as client:
            resp = client.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))

    def test_user_show(self):
        """Testing if user shows"""
        with self.client as client:
            resp = client.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))

    def test_user_search(self):
        """Testing searching users"""
        with self.client as client:
            resp = client.get("/users?q=testuser")

            self.assertIn("@testuser", str(resp.data))
            self.assertNotIn("@user1", str(resp.data))
            self.assertNotIn("@user2", str(resp.data))
            self.assertNotIn("@user3", str(resp.data))

    def test_user_likes(self):
        """Testing user likes"""
        with app.app_context():
            message1 = Message(text="New message 1", user_id=self.testuser_id)
            message2 = Message(text="New message 2", user_id=self.testuser_id)

            db.session.add_all([message1, message2])
            db.session.commit()

            self.assertIsNotNone(message1.id)
            self.assertIsNotNone(message2.id)

            like1 = Likes(user_id=self.testuser_id, message_id=message1.id)
            like2 = Likes(user_id=self.testuser_id, message_id=message2.id)

            db.session.add_all([like1, like2])
            db.session.commit()

            testuser = User.query.get(self.testuser_id)
            user_likes = testuser.liked_messages

            self.assertIn(like1, user_likes)
            self.assertIn(like2, user_likes)

    def test_add_like(self):
        """Testing add likes"""
        with app.app_context():
            with self.client as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user1_id

                m = Message.query.get(1111)
                self.assertIsNotNone(m)

                resp = client.post(f"/users/add_like/{m.id}", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id == 1111).all()
                self.assertEqual(len(likes), 1)
                self.assertEqual(likes[0].user_id, self.user1_id)

    def test_cannot_like_own_message(self):
        """Test that a user cannot like their own message."""
        with app.app_context():
            with self.client as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser_id

                m = Message.query.get(1111)
                self.assertIsNotNone(m)

                resp = client.post(f"/users/add_like/{m.id}", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id == 1111).all()
                self.assertEqual(len(likes), 0)


    def test_remove_like(self):
        """Test that a user can unlike a message they have liked."""
        with app.app_context():
            
            with self.client as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser_id

                m = Message.query.get(1111)
                self.assertIsNotNone(m)

                resp = client.post(f"/users/add_like/{m.id}", follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                resp = client.post(f'/users/add_like/{m.id}', follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

                likes = Likes.query.filter(Likes.message_id == 1111).all()
                self.assertEqual(len(likes), 0)

