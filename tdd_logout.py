from classes import Logout, LogoutController, UserSession
import unittest


class TestLogin(unittest.TestCase):

    def setUp(self):
        session = {"username":"owner1"}
        self.boundary = Logout(session)

    def test_A_editSession(self):
        # editSession will remove "username" in session
        session = self.boundary.controller.editSession(self.boundary.session, "owner1")
        self.assertNotIn("username", session)


if __name__ == "__main__":
    unittest.main()
