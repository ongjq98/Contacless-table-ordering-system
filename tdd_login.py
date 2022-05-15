from classes import LoginPage, LoginPageController, UserAccount
import unittest


class TestLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #print("setUpClass : initialize login boundary")
        cls.boundary = LoginPage()

    def test_A_Manager_getCredentials(self):
        print("Test A : LoginPage.getCredentials() - Manager")

        # correct type, correct username, correct password -- True
        request_form = {"type": "manager", "username": "manager234", "password": "manager234"}
        self.assertTrue(self.boundary.controller.getCredentials(request_form))

        # correct type, correct username, incorrect password -- False
        request_form = {"type": "manager", "username": "manager234", "password": "manager"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "manager", "username": "manager10", "password": "manager234"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "manager", "username": "manager10", "password": "manager234"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, incorrect password -- False
        request_form = {"type": "manager", "username": "manager10", "password": "manager10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # incorrect type, correct username, correct password -- False
        request_form = {"type": "staff", "username": "manager234", "password": "manager234"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))


    def test_B_Staff_getCredentials(self):
        print("\nTest B : LoginPage.getCredentials() - Staff")

        # correct type, correct username, correct password -- True
        request_form = {"type": "staff", "username": "staff1", "password": "staff1"}
        self.assertTrue(self.boundary.controller.getCredentials(request_form))

        # correct type, correct username, incorrect password -- False
        request_form = {"type": "staff", "username": "staff1", "password": "staff10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "staff", "username": "staff10", "password": "staff1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "staff", "username": "staff10", "password": "staff1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, incorrect password -- False
        request_form = {"type": "staff", "username": "staff10", "password": "staff10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # incorrect type, correct username, correct password -- False
        request_form = {"type": "admin", "username": "staff1", "password": "staff1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))


    def test_C_Admin_getCredentials(self):
        print("\nTest C : LoginPage.getCredentials() - Admin")

        # correct type, correct username, correct password -- True
        request_form = {"type": "admin", "username": "admin1", "password": "admin1"}
        self.assertTrue(self.boundary.controller.getCredentials(request_form))

        # correct type, correct username, incorrect password -- False
        request_form = {"type": "admin", "username": "admin1", "password": "admin10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "admin", "username": "admin10", "password": "admin1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "admin", "username": "admin10", "password": "admin1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, incorrect password -- False
        request_form = {"type": "admin", "username": "admin10", "password": "admin10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # incorrect type, correct username, correct password -- False
        request_form = {"type": "owner", "username": "admin1", "password": "admin1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))


    def test_D_Owner_getCredentials(self):
        print("\nTest D : LoginPage.getCredentials() - Owner")

        # correct type, correct username, correct password -- True
        request_form = {"type": "owner", "username": "owner1", "password": "owner1"}
        self.assertTrue(self.boundary.controller.getCredentials(request_form))

        # correct type, correct username, incorrect password -- False
        request_form = {"type": "owner", "username": "owner1", "password": "owner10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "owner", "username": "owner10", "password": "owner1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, correct password -- False
        request_form = {"type": "owner", "username": "owner10", "password": "owner1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # correct type, incorrect username, incorrect password -- False
        request_form = {"type": "owner", "username": "owner10", "password": "owner10"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

        # incorrect type, correct username, correct password -- False
        request_form = {"type": "manager", "username": "owner1", "password": "owner1"}
        self.assertFalse(self.boundary.controller.getCredentials(request_form))

if __name__ == "__main__":
    unittest.main()
