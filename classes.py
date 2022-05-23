### IMPORTS ###
import decimal
from re import sub
from decimal import Decimal
from inspect import _void
from random import vonmisesvariate
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime


### POSTGRESQL CONFIG ###
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'


#####----- ALL USERS (LOGIN) -----#####

### LOGIN BOUNDARY ###
class LoginPage:
    def __init__(self) -> None:
        self.controller = LoginPageController()
        self.user_exist = False

    def loginTemplate(self):
        # get all profiles
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()

        return render_template("login.html", profiles=profiles)

    def redirectPage(account_type):
        default_profiles = ["admin", "manager", "owner", "staff"]
        if account_type not in default_profiles:
            return redirect(url_for("otherProfiles", type=account_type))
        else:
            return redirect(url_for(account_type))


### LOGIN CONTROLLER ###
class LoginPageController:
    def __init__(self) -> None:
        self.entity = UserAccount()

    def getCredentials(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.password = request_form["password"]
        self.entity.account_type = request_form["type"]
        return self.entity.doesUserExist()

    def userExist(self) -> None:
        self.user_exist = True

    def userNotExist(self) -> None:
        self.user_exist = False


### LOGIN ENTITY BELOW WITH ADMIN ENTITY ###



#####----- ALL USERS (LOGIN) -----#####

### LOGOUT BOUNDARY ###
class Logout:
    def __init__(self, session) -> None:
        self.session = session
        self.username = session["username"]
        self.controller = LogoutController(self.session, self.username)

    def logUserOut(self):
        self.session = self.controller.editSession(self.session, self.username)
        flash(f"{self.username} logged out!")
        return redirect(url_for("index"))

### LOGOUT CONTROLLER ###
class LogoutController:
    def __init__(self, session, username) -> None:
        self.session = session
        self.username = session["username"]
        self.entity = UserSession()

    def editSession(self, session, username):
        return self.entity.checkUserInSession(session, username)

### LOGOUT ENTITY ###
class UserSession:
    def checkUserInSession(self, session, username):
        self.session = session
        if "username" in session and session["username"] == username:
            return self.removeUserSession(username)

    def removeUserSession(self, username):
        self.session.pop("username")
        return self.session



#####----- ADMIN PROFILES -----#####

### ADMIN PROFILE BOUNDARY ###
class AdminProfilePage:
    def __init__(self) -> None:
        self.controller = AdminProfileController()

    def adminTemplate(self):
        return render_template("admin.html")

    def adminTemplateCreateProfile(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT Column_name FROM Information_schema.columns WHERE Table_name like 'profile'")
                profile_function = cursor.fetchall()
                del profile_function[0]
                return render_template("adminCreateP.html", profile_function=profile_function)

    def adminTemplateEditProfile(self):
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT Column_name FROM Information_schema.columns WHERE Table_name like 'profile'")
                profile_function = cursor.fetchall()
                del profile_function[0]
                return render_template("adminEditP.html", profile_function=profile_function)

    def adminTemplateViewProfile(self):
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profile_name = cursor.fetchall()
                return render_template("adminViewP.html", profile_name=profile_name)

    def adminProfileViewResult(self, data):
        return render_template("adminViewPResult.html", data=data)

    def adminTemplateSearchProfile(self):
        return render_template("adminSearchP.html")

    def adminProfileSearchResult(self, data):
        return render_template("adminSearchPResult.html", data=data)

    def adminTemplateSuspendProfile(self):
        return render_template("adminSuspendP.html")


### ADMIN PROFILE CONTROLLER ###
class AdminProfileController:
    def __init__(self) -> None:
        self.entity = UserProfile()

    def createProfileInfo(self, request_form) -> bool:
        self.entity.profile_name = request_form["profile_name"]
        self.entity.statistics = (request_form["grant_view_statistics"])
        self.entity.cart = request_form["grant_view_edit_cart"]
        self.entity.accounts = request_form["grant_view_edit_accounts"]
        self.entity.menu = request_form["grant_view_edit_menu"]
        self.entity.coupon = request_form["grant_view_edit_coupon"]
        return self.entity.createProfile()

    def editProfileInfo(self, request_form) -> bool:
        self.entity.profile_name = request_form["profile_name"]

        self.entity.new_profile_name = request_form["new_profile_name"]
        self.entity.statistics = (request_form["grant_view_statistics"])
        self.entity.cart = request_form["grant_view_edit_cart"]
        self.entity.accounts = request_form["grant_view_edit_accounts"]
        self.entity.menu = request_form["grant_view_edit_menu"]
        self.entity.coupon = request_form["grant_view_edit_coupon"]
        return self.entity.editProfile()

    def viewProfileInfo(self, request_form) -> list:
        self.entity.profile_name = request_form["submit"]
        return self.entity.viewProfile()

    def searchProfileInfo(self, request_form) -> bool:
        self.entity.profile_name = request_form["profile_name"]
        return self.entity.searchProfile()

    def getProfileInfo(self, request_form) -> list:
        self.entity.profile_name = request_form["profile_name"]
        return self.entity.getProfile()

    def suspendProfileInfo(self, request_form) -> bool:
        self.entity.profile_name = request_form["profile_name"]
        return self.entity.suspendProfile()


### ADMIN PROFILE ENTITY ###
class UserProfile:
    def getProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM profile WHERE profile_name='{self.profile_name}'")
                db.commit()
                return cursor.fetchall()

    def createProfile(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result == None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"INSERT INTO profile (profile_name, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon) VALUES (%s, %s, %s, %s, %s, %s)", (self.profile_name, self.statistics, self.cart, self.accounts, self.menu, self.coupon))
                            db.commit()
                    return True
                else:
                    return False

    def editProfile(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"UPDATE profile SET profile_name=%s, grant_view_statistics=%s, grant_view_edit_cart=%s, grant_view_edit_accounts=%s, grant_view_edit_menu=%s, grant_view_edit_coupon=%s WHERE profile_name=%s", (self.new_profile_name, self.statistics, self.cart, self.accounts, self.menu, self.coupon, self.profile_name))
                            db.commit()
                    return True
                else:
                    return False

    def viewProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM profile WHERE profile_name='{self.profile_name}'")
                db.commit()
                return cursor.fetchall()

    def searchProfile(self) -> bool:
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def suspendProfile(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile WHERE profile_name='{self.profile_name}'")
                result = cursor.fetchone()
                db.commit()
                if result != None: #check if profile exist
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"DELETE FROM profile WHERE profile_name='{self.profile_name}'")
                            db.commit()
                    return True
                else:
                    return False


### ADMIN ACCOUNT BOUNDARY ###
class AdminPage:
    def __init__(self) -> None:
        self.controller = AdminPageController()

    def adminTemplate(self, username):
        return render_template("admin.html", username=username)

    def adminTemplateCreateAccount(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()
                return render_template("adminCreateA.html", profiles=profiles)

    def adminTemplateEditAccount(self):
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()
                return render_template("adminEditA.html", profiles=profiles)

    def adminTemplateViewAccount(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, profile FROM users")
                profiles = cursor.fetchall()
                return render_template("adminViewA.html", profiles=profiles)

    def adminAccountViewResult(self, data):
        return render_template("adminViewAResult.html", data=data)

    def adminTemplateSearchAccount(self):
        return render_template("adminSearchA.html")

    def adminAccountSearchResult(self, username, account_type):
        return render_template("adminSearchAResult.html", username=username, account_type=account_type)

    def adminTemplateSuspendAccount(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()
                return render_template("adminSuspendA.html", profiles=profiles)


### ADMIN ACCOUNT CONTROLLER ###
class AdminPageController:
    def __init__(self) -> None:
        self.entity = UserAccount()

    def getDatabyUandTInfo(self, request_form) -> list:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.getDatabyUandT()

    def getDatabyUInfo(self, request_form) -> list:
        self.entity.username = request_form["username"]
        return self.entity.getDatabyU()

    def createAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.password = request_form["password"]
        self.entity.account_type = request_form["type"]
        return self.entity.createAccount()

    def editAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]

        self.entity.new_username = request_form["NewUsername"]
        self.entity.new_password = request_form["NewPassword"]
        self.entity.new_account_type = request_form["NewType"]
        return self.entity.editAccount()

    def viewAccountInfo(self, request_form) -> list:
        ss = request_form["submit"].split(",")
        self.entity.username = ss[0]
        self.entity.account_type = ss[1]
        return self.entity.viewAccount()

    def searchAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        return self.entity.searchAccount()

    def suspendAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.suspendAccount()


### LOGIN & ADMIN ACCOUNT ENTITY ###
class UserAccount:
    def doesUserExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (self.username, self.password, self.account_type))
                result = cursor.fetchone()
                db.commit()

                if result != None: return True
                else: return False

    def getDatabyUandT(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                    db.commit()
                    return cursor.fetchall()

    def getDatabyU(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute(f"SELECT username, password, profile FROM users WHERE username='{self.username}'")
                    db.commit()
                    return cursor.fetchall()

    def createAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result == None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"INSERT INTO users (profile, username, password) VALUES (%s, %s, %s)", (self.account_type, self.username, self.password))
                            db.commit()
                    return True
                else:
                    return False

    def editAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"UPDATE users SET username=%s, password=%s, profile=%s WHERE username=%s AND profile=%s", (self.new_username, self.new_password, self.new_account_type, self.username, self.account_type))
                        db.commit()
                    return True
                else:
                    return False

    def viewAccount(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                db.commit()
                return cursor.fetchall()

    def searchAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username='{self.username}'")
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def suspendAccount(self) -> bool:
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                            cursor.execute(f"DELETE FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                        db.commit()
                    return True
                else:
                    return False

#### END OF ADMIN ####


#####----- STAFF -----#####

### STAFF BOUNDARY ###
class StaffPage:
    def __init__(self) -> None:
        self.controller = StaffPageController()

    def staffTemplate(self, username):
        return render_template("staff.html", username=username)

    def staffTemplateViewCart(self, data):
        return render_template("staffViewCart.html", data=data)

    def staffTemplateViewOrders(self, data):
        return render_template("staffViewOrders.html", data=data)

    def staffSearchCart(self, data):
        return render_template("staffSearchCart.html", data=data)

    def staffSearchOrder(self, data):
        return render_template("staffSearchOrder.html",data=data)


### STAFF CONTROLLER ###
class StaffPageController:
    def __init__(self) -> None:
        self.entity = CartDetails()

    def getCart(self) -> list:
        #self.entity.table_id=request_form["table_id"]
        return self.entity.retrieveCart()

    def searchCart(self,search_cart_id) -> list:
        return self.entity.searchSpecificCart(search_cart_id)


    def getOrders(self,cart_id) -> list:
        print("Inside getOrders")
        return self.entity.retrieveOrders(cart_id)

    def searchOrder(self,current_cart_id,search_order_id) -> list:
        return self.entity.searchSpecificOrder(current_cart_id,search_order_id)

    def updateOrder(self,current_cart_id,order_id, item_id,quantity) -> list:
        return self.entity.updateSpecificOrder(current_cart_id,order_id,item_id,quantity)

    def deleteOrder(self,current_cart_id, order_id) -> list:
        return self.entity.deleteSpecificOrder(current_cart_id,order_id)

    def insertOrder(self,current_cart_id, item_id,item_quantity,is_it_fulfilled) -> list:
        return self.entity.insertSpecificOrder(current_cart_id, item_id,item_quantity,is_it_fulfilled)

    def toFulfill(self,curret_cart_id,order_id) -> list:
        return self.entity.fulfillSpecificOrder(curret_cart_id, order_id)


### STAFF ENTITY ###
class CartDetails:
    def retrieveCart(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM public.""cart"" where is_it_paid=false; ")
                result = cursor.fetchall()
                db.commit()
                return result

    def searchSpecificCart(self,search_cart_id):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM public.""cart"" where is_it_paid=false and cart_id=%s; ", (search_cart_id, ))
                result = cursor.fetchone()
                db.commit()
                if not result:
                    return "Cart does not exist"
                else:
                    return result


    def retrieveOrders(self,cart_id):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (cart_id, ))
                result = cursor.fetchall()
                db.commit()
                return result

    def searchSpecificOrder(self,current_cart_id,search_order_id):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" where order_id=%s AND cart_id=%s; ", (search_order_id,current_cart_id, ))
                result = cursor.fetchone()
                db.commit()
                if not result:
                    return "Order does not exist"
                else:
                    return result

    def updateSpecificOrder(self,current_cart_id,order_id,item_id,quantity):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"SELECT item_id,name,price FROM public.menuitems WHERE item_id= %s;",(item_id, ))
                ar = cursor.fetchone()
                cursor.execute(f"UPDATE public.""order"" SET item_id = %s, quantity = %s, name=%s, price=%s WHERE order_id = %s;", (ar[0], quantity, ar[1], ar[2]*float(quantity),order_id,   ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price,is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                return result


    def deleteSpecificOrder(self,current_cart_id,order_id):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"DELETE FROM public.""order"" WHERE order_id = %s;", (order_id, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price,is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                return result

    def insertSpecificOrder(self,current_cart_id, item_id,item_quantity,is_it_fulfilled):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(f"SELECT item_id,name,price FROM public.menuitems WHERE item_id= %s;",(item_id, ))
                ar = cursor.fetchone()
                cursor.execute(f"INSERT INTO public.""order""(item_id, cart_id, name, quantity, price, ordered_time, is_it_fulfilled) VALUES (%s, %s, %s, %s, %s, %s, %s);",(ar[0],current_cart_id,ar[1],item_quantity,ar[2]*float(item_quantity),dt,is_it_fulfilled, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                return result

    def fulfillSpecificOrder(self,current_cart_id,order_id):
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"UPDATE public.""order"" SET is_it_fulfilled = true WHERE order_id = %s;", (order_id, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                return result


#####----- CUSTOMER -----#####

### CUSTOMER BOUNDARY ###
class CustomerPage:
    def __init__(self) -> None:
        self.controller = CustomerPageController()

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]
        template = self.controller.serveSelectedPage(self.button_id)
        return template

    def customerHomePage(self):
        return render_template("customer.html", cartId=session.get("cartId", "") , tableId=session.get("tableId", ""))

    def addOrderPage(self, menu):
        return render_template("add_order.html", data=menu)

    def editOrderPage(self, menu):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT item_id, name, quantity, price FROM public."order" WHERE cart_id = %s', (session["cartId"],))
                old_items = cursor.fetchall()
        return render_template("editOrder.html", old_items=old_items, menu=menu, tableId = session["tableId"], cartId = session["cartId"], phone_no = session["phone_no"])

    def deleteOrderPage(self):
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT item_id, name, quantity, price FROM public."order" WHERE cart_id = %s', (session["cartId"],))
                order_list = cursor.fetchall()
        return render_template("deleteOrder.html",tableId = session["tableId"], cartId = session["cartId"], phone_no = session["phone_no"], order_list = order_list)

    def viewCart(self):
        return render_template("viewMenu.html")

    def payment(self):
        return render_template("payment.html")

    def redirectToCustomerPage(self):
        return redirect(url_for("index"))


### CUSTOMER CONTROLLER ###
class CustomerPageController:
    def __init__(self) -> None:
        self.entity = Orders()

    #from index page to navigate to which page
    def serveSelectedPage(self, button_id):
        if request.form["button_type"] == "b1":
            return redirect(url_for("add_order"))
        elif request.form["button_type"] == "b2":
            return redirect(url_for("editOrder"))
        elif request.form["button_type"] == "b3":
            return redirect(url_for("deleteOrder"))
        elif request.form["button_type"] == "b4":
            return redirect(url_for("payment"))
        elif request.form["button_type"] =='return':
            return redirect(url_for("index"))

    def getOrderlistToAdd(self, form_request, request_list) -> None:
        self.entity.phone_no = form_request["phone_no"]
        self.entity.item_id = request_list("item_id[]")
        self.entity.table_id = form_request["table_id"]
        self.entity.item_name = request_list("item_name[]")
        self.entity.item_quantity = request_list("item_quantity[]")
        self.entity.item_price = request_list("item_price[]")
        #check if customer exist, if exist increment visit count and last visit date

        self.entity.addOrders()


    def getOrderlistToUpdateAndAdd(self, form_request, request_list) -> None:
        self.entity.cart_id = session["cartId"]
        self.entity.table_id = form_request["table_id"]
        self.entity.phone_id = form_request["phone_no"]

        #To update quantity to database
        self.entity.item_id_old = request_list("item_id_old[]")
        self.entity.item_name_old = request_list("item_name_old[]")
        self.entity.item_quantity_old = request_list("item_quantity_old[]")
        self.entity.item_price_old = []

        #To add in new orders to database
        self.entity.item_id_new = request_list("item_id_new[]")
        self.entity.item_name_new = request_list("item_name_new[]")
        self.entity.item_quantity_new = request_list("item_quantity_new[]")
        self.entity.item_price_new = request_list("item_price_new[]")

        #add orders into database
        self.entity.newOrders()
        self.entity.updateOrders()

    def getOrderlistToDelete(self, request_list) -> None :
        self.entity.toDelete = request_list("toDelete[]")

        #To delete  from database
        self.entity.deleteOrders()

    def getpaymentDetails(self, form_request) -> None:
        self.entity.coupon_name = form_request["coupon_name"]

        if self.entity.itemFulfilmentAndCouponValidity():
            self.entity.setCartToPaid()
        else:
            print("No payment made")

    #search
    def getSearchQuery(self, request) -> None:
        self.entity.query = request["query"]
        return self.entity.searchMenu()

    #view
    def getMenu(self):
        return self.entity.retrieveMenu()

### CUSTOMER ENTITY ###
class Orders:
    ### Customer Use Case 1 - addOrders, ifCustomerExist, updateCustLastVisitAndCount, insertNewCust ###
    def addOrders(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM customer WHERE phone_no = %s;" , (self.phone_no,))
                result = cursor.fetchone()
                print(result)
                db.commit()
                if result == None:
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(f"INSERT INTO customer(phone_no, no_of_visits, last_visit) VALUES(%s,%s,%s)", (self.phone_no, 1, dt))
                    db.commit()
                else:
                    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(f"UPDATE customer SET no_of_visits = no_of_visits + 1 WHERE phone_no = %s" , (self.phone_no,))
                    db.commit()
                    cursor.execute(f"UPDATE customer SET last_visit = %s WHERE phone_no = %s" , (dt,self.phone_no))
                    db.commit()

                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(f"INSERT INTO cart(table_id, phone_no, start_time, is_it_paid) VALUES(%s, %s, %s, %s) RETURNING cart_id", (self.table_id, self.phone_no, dt, False))
                db.commit()
                added_cart_id = cursor.fetchone()[0]
                self.cart_id = added_cart_id
                for i in range(len(self.item_name)):
                    total_cost = Decimal(sub(r'[^\d.]', '', (self.item_price)[i])) * int((self.item_quantity)[i])
                    print(total_cost)
                    cursor.execute(f'INSERT INTO public."order"(item_id, cart_id, name, quantity, price, ordered_time, is_it_fulfilled) VALUES(%s, %s, %s, %s, %s, %s, %s)', ((self.item_id)[i], added_cart_id, (self.item_name)[i], (self.item_quantity)[i], total_cost, dt, False))
                    cursor.execute(f'UPDATE public."menuitems" SET ordered_count = ordered_count + %s WHERE name=%s', (int((self.item_quantity)[i]),(self.item_name)[i]))
                    db.commit()
    '''
    def addOrders(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(f"INSERT INTO cart(table_id, phone_no, start_time, is_it_paid) VALUES(%s, %s, %s, %s) RETURNING cart_id", (self.table_id, self.phone_no, dt, False))
                db.commit()
                added_cart_id = cursor.fetchone()[0]
                self.cart_id = added_cart_id
                for i in range(len(self.item_name)):
                    total_cost = Decimal(sub(r'[^\d.]', '', (self.item_price)[i])) * int((self.item_quantity)[i])
                    print(total_cost)
                    cursor.execute(f'INSERT INTO public."order"(item_id, cart_id, name, quantity, price) VALUES(%s, %s, %s, %s, %s)', ((self.item_id)[i], added_cart_id, (self.item_name)[i], (self.item_quantity)[i], total_cost))
                    db.commit()


    def ifCustomerExist(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM customer WHERE phone_no = %s;" , (self.phone_no,))
                result = cursor.fetchone()
                print(result)
                db.commit()
                if result == None:
                    return False
                else:
                    return True

    def updateCustLastVisitAndCount(self) -> None:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"UPDATE customer SET no_of_visits = no_of_visits + 1 WHERE phone_no = %s" , (self.phone_no,))
                db.commit()
                cursor.execute(f"UPDATE customer SET last_visit = %s WHERE phone_no = %s" , (dt,self.phone_no))
                db.commit()

    def insertNewCust(self) -> None:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"INSERT INTO customer(phone_no, no_of_visits, last_visit) VALUES(%s,%s,%s)", (self.phone_no, 1, dt))
                db.commit()
    '''
    ### Customer Use Case 2 - newOrders, updateOrders ###
    def newOrders(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for i in range(len(self.item_name_new)):
                    total_cost = decimal(sub(r'[^\d.]', '', (self.item_price_new)[i])) * int((self.item_quantity_new)[i])

                    cursor.execute(f'INSERT INTO public."order"(item_id, cart_id, name, quantity, price) VALUES(%s, %s, %s, %s, %s)', ((self.item_id_new)[i], self.cart_id, (self.item_name_new)[i], (self.item_quantity_new)[i], total_cost))
                    db.commit()

    def updateOrders(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for i in range(len(self.item_name_old)):
                    cursor.execute(f'SELECT price FROM menuitems WHERE name=%s', ((self.item_name_old)[i], ))
                    item_price_per_item = cursor.fetchall()[0][0]
                    total_cost = int((self.item_quantity_old)[i]) * float(item_price_per_item)
                    cursor.execute(f'UPDATE public."order" SET quantity=%s, price=%s WHERE item_id=%s', ((self.item_quantity_old)[i], total_cost,(self.item_id_old)[i]))
                    db.commit()

    def deleteOrders(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for i in range(len(self.toDelete)):
                    cursor.execute(f'DELETE FROM public."order" WHERE name = %s AND cart_id = %s;', ((self.toDelete)[i], self.cart_id))
                    db.commit()

    #Use case customer payemnt - areAllItemsFulfilled, doesCouponExistAndValid, setCartToPaid
    def areAllItemsFulfilled(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT * FROM public."order" WHERE cart_id=%s;', (self.cart_id))
                result = cursor.fetchall()
                list_items_fulfilled = []
                for i in range(len(result)):
                    list_items_fulfilled.append(result[i][7])

                if False in  list_items_fulfilled:
                    return True
                else:
                    return False

    def doesCouponExistAndValid(self) -> bool:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                #check if coupon exist
                cursor.execute(f'SELECT * FROM public."coupon" WHERE name = %s', (self.coupon_name,))
                result = cursor.fetchone()
                if result != None:
                    #if coupon exist, check the coupon expire or not using the range for coupon start datetime and end datetime
                    if datetime.strptime(result[2],'%Y-%m-%d %H:%M:%S') <= dt <= datetime.strptime(result[3],'%Y-%m-%d %H:%M:%S'):
                        cursor.execute(f'UPDATE public."cart" SET coupon_discout = %s WHERE cart_id= %s', (result[4],self.cart_id,))
                        db.commit()
                        return True
                return False

    def setCartToPaid(self) -> None:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'UPDATE public."cart" SET is_it_paid = true WHERE cart_id= %s', (self.cart_id,))
                cursor.execute(f'UPDATE public."cart" SET end_time = %s WHERE cart_id= %s', (dt, self.cart_id,))
                db.commit()

    def isMenuEmpty(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems")
                result = cursor.fetchone()
                db.commit()
                if result == None:
                    return True
                else:
                    return False

    def searchMenu(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f'SELECT * FROM menuitems WHERE name = %s OR item_id = %s', (self.query, self.query) )
                return cursor.fetchall()

    def retrieveMenu(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems")
                return cursor.fetchall()

#####----- OWNER -----#####

### OWNER BOUNDARY ###
class OwnerPage:
    def __init__(self) -> None:
        self.controller = OwnerPageController()

    def ownerHomePage(self, username):
        return render_template("owner.html", username=username)

    def getDatePage(self):
        return render_template("getDatePage.html")

    def getWeeklyDatePage(self):
        return render_template("getWeeklyDatePage.html")

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]

        if self.button_id == "b1":
            return redirect(url_for("display_H_avg_spend"))
        elif self.button_id == "b2":
            return redirect(url_for("display_D_avg_spend"))
        elif self.button_id == "b3":
            return redirect(url_for("display_W_avg_spend"))
        elif self.button_id == "b4":
            return redirect(url_for("display_H_frequency"))
        elif self.button_id == "b5":
            return redirect(url_for("display_D_frequency"))
        elif self.button_id == "b6":
            return redirect(url_for("display_W_frequency"))
        elif self.button_id == "b7":
            return redirect(url_for("display_H_preference"))
        elif self.button_id == "b8":
            return redirect(url_for("display_D_preference"))
        elif self.button_id == "b9":
            return redirect(url_for("display_W_preference"))



    def displayHourlySpendingReport(self,date_request, data):
        return render_template("HourlySpending.html", totalHours=6, date_request = date_request, data = data)

    def displayDailySpendingReport(self,date_request, data):
        return render_template("DailySpending.html", date_request = date_request, data = data)

    def displayWeeklySpendingReport(self,date_request,start_date,end_date,data, totalRev, totalCust):
        return render_template("WeeklySpending.html", date_request = date_request,start_date = start_date, end_date = end_date, data = data, totalRev = totalRev, totalCust=totalCust)

    def displayHourlyFrequencyReport(self,date_request,data):
        return render_template("HourlyFrequency.html", date_request = date_request, data = data)

    def displayDailyFrequencyReport(self,date_request,data):
        return render_template("DailyFrequency.html", date_request = date_request, data = data)

    def displayWeeklyFrequencyReport(self,date_request,start_date, end_date, data, total):
        return render_template("WeeklyFrequency.html", week = date_request, start_date=start_date, end_date=end_date, data = data, total=total)

    def displayHourlyPreferenceReport(self, year, month, day, list):
        return render_template("HourlyPreference.html", year=year, month=month, day=day, hourly_preference_list=list)

    def displayDailyPreferenceReport(self, year, month, day, list):
        return render_template("DailyPreference.html", year=year, month=month, day=day, result=list)

    def displayWeeklyPreferenceReport(self, week, year, start, end, result):
        return render_template("WeeklyPreference.html", week=week, year=year, start=start, end=end, result=result)


### OWNER CONTROLLER ###
class OwnerPageController:
    def __init__(self) -> None:
        self.entity = OwnerReport()

    def getHourlySpending(self, date_request) -> list:
        return self.entity.generateHourlySpendingReport(date_request)

    def getDailySpending(self, start, end) -> list:
        return self.entity.generateDailySpendingReport(start,end)

    def getWeeklySpending(self, start, end) -> list:
        return self.entity.generateWeeklySpendingReport(start,end)

    def getHourlyFrequency(self, year, month, day) -> list:
        return self.entity.generateHourlyFrequencyReport(year,month,day)

    def getDailyFrequency(self, start, end) -> list:
        return self.entity.generateDailyFrequencyReport(start, end)

    def getWeeklyFrequency(self, start, end) -> list:
        return self.entity.generateWeeklyFrequencyReport(start,end)

    def getHourlyPreference(self, year, month, day) -> list:
        return self.entity.generateHourlyPreferenceReport(year, month, day)

    def getDailyPreference(self, year, month, day) -> list:
        return self.entity.generateDailyPreferenceReport(year, month, day)

    def getWeeklyPreference(self, year, week) -> list:
        return self.entity.generateWeeklyPreferenceReport(year, week)


### OWNER ENTITY ###
class OwnerReport:
    #HourlySpending==========
    def generateHourlySpendingReport(self, date_request):
        #get total earnings and customers
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT sum(total_amount), count(cart_id) from cart where start_time between '{date_request} 12:00:00' and '{date_request} 17:59:59'")
                data = cursor.fetchall()
        return data

    #End of HourlySpending========

    #DailySpending==========
    def generateDailySpendingReport(self, start, end):
        #get total earnings and customers
        data =[]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for day in range(1,8):
                    cursor.execute("SELECT sum(total_amount), count(cart_id) FROM cart WHERE start_time between '{}' and '{}'".format(start, end))
                    temp = cursor.fetchall()
                    data.extend(temp)
                    start = start - timedelta(days=1)
                    end = end - timedelta(days=1)
                        #print(f"data in loop: {data}")
        #print(data)
        return data
    #End of DailySpending========

    #WeeklySpending==========
    def generateWeeklySpendingReport(self, start, end):
        #get total earnings and customers
        data =[]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for day in range(1,8):
                    cursor.execute("SELECT sum(total_amount), count(cart_id) FROM cart WHERE start_time between '{}' and '{}'".format(start, end))
                    temp = cursor.fetchall()
                    data.extend(temp)
                    start = start + timedelta(days = 1)
                    end = end + timedelta(days=1)
        return data
    #End of WeeklySpending========

    #HourlyFrequency==========
    def generateHourlyFrequencyReport(self, year, month, day):
        operating_hours = range(12,18)
        data = []
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for hour in operating_hours:
                    start = datetime(year, month, day, hour, 0, 0)
                    end = start + timedelta(minutes=59, seconds= 59)
                    cursor.execute("SELECT count(cart_id) FROM cart WHERE start_time between '{}' and '{}'".format(start, end))
                    temp = cursor.fetchall()
                    temp.append(hour * 100)
                    data.append(temp) # temp = [1400, [1]]
                    #print(f'this is temp: {temp}')
                    #print(f'this is data: {data}')
        return data
    #End of HourlyFrequency========

    #DailyFrequency==========
    def generateDailyFrequencyReport(self, start, end):
        data =[]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for days in range(1,8):
                    cursor.execute("SELECT count(cart_id) from cart where start_time between '{}' and '{}'".format(start, end))
                    temp = cursor.fetchall()
                    data.extend(temp)
                    start = start - timedelta(days=1)
                    end = end - timedelta(days=1)
        return data

    #End of DailyFrequency========

    #WeeklyFrequency==========
    def generateWeeklyFrequencyReport(self, start, end):
        data =[]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    for day in range(1,8):
                        cursor.execute("SELECT count(cart_id) FROM cart WHERE start_time between '{}' and '{}' ".format(start, end))
                        temp = cursor.fetchall()
                        data.extend(temp)
                        start = start + timedelta(days=1)
                        end = end + timedelta(days=1)
                        #print(f"data in loop: {data}")
        #print(data)
        return data
    #End of WeeklyFrequency========
    def generateHourlyPreferenceReport(self, year, month, day) -> list:
        operating_hours = range(12,18)
        hourly_preference_list = []

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for hour in operating_hours:
                    start = datetime(year, month, day, hour, 0, 0)
                    end = start + timedelta(minutes=60)
                    cursor.execute("SELECT name, quantity from public.\"order\" WHERE ordered_time between '{}' and '{}'".format(start, end))
                    name_quantity = cursor.fetchall()

                    name_quantity_dictionary = {}
                    for pair in name_quantity:
                        item_name = pair[0]
                        item_quantity = pair[1]
                        if item_name in name_quantity_dictionary:
                            name_quantity_dictionary[item_name] += item_quantity
                        else:
                            name_quantity_dictionary[item_name] = item_quantity

                    if name_quantity_dictionary != {}: # if dict is not empty
                        most_ordered_item = max(name_quantity_dictionary, key=name_quantity_dictionary.get)
                        most_quantity = name_quantity_dictionary[most_ordered_item]
                        hourly_preference = [hour, most_ordered_item, most_quantity]

                        hourly_preference_list.append(hourly_preference)
                    else:
                        hourly_preference_list.append([hour, "-", "-"])
        return hourly_preference_list


    def generateDailyPreferenceReport(self, year, month, day) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                start = datetime(year, month, day, 0, 0, 0)
                end = datetime(year, month, day, 23, 59, 59)

                cursor.execute("SELECT name, quantity from public.\"order\" WHERE ordered_time between '{}' and '{}'".format(start, end))
                name_quantity = cursor.fetchall()

                name_quantity_dictionary = {}
                for pair in name_quantity:
                    item_name = pair[0]
                    item_quantity = pair[1]
                    if item_name in name_quantity_dictionary:
                        name_quantity_dictionary[item_name] += item_quantity
                    else:
                        name_quantity_dictionary[item_name] = item_quantity

                name_quantity_descending = sorted(name_quantity_dictionary.items(), key=lambda x:x[1], reverse=True)
        return name_quantity_descending


    def generateWeeklyPreferenceReport(self, year:int, week:int) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                start_of_week = datetime(year,1,3,0,0,0) + timedelta(weeks=week-1)
                end_of_week = start_of_week + timedelta(weeks=1)

                cursor.execute("SELECT name, quantity from public.\"order\" WHERE ordered_time between '{}' and '{}'".format(start_of_week, end_of_week))
                name_quantity = cursor.fetchall()

                name_quantity_dictionary = {}
                for pair in name_quantity:
                    item_name = pair[0]
                    item_quantity = pair[1]
                    if item_name in name_quantity_dictionary:
                        name_quantity_dictionary[item_name] += item_quantity
                    else:
                        name_quantity_dictionary[item_name] = item_quantity

                name_quantity_descending = sorted(name_quantity_dictionary.items(), key=lambda x:x[1], reverse=True)
        return name_quantity_descending




#####----- MANAGER -----#####
### MANAGER BOUNDARY ###
class ManagerPage:
    def __init__(self) -> None:
        self.controller = ManagerController()

    def managerHomePage(self, username):
        return render_template("manager.html", username=username)

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]

        if request.form["button_type"] == "a1":
            return redirect(url_for("managerviewItem"))
        elif request.form["button_type"] == "a3":
            return redirect(url_for("managerupdateItem"))
        elif request.form["button_type"] == "a4":
            return redirect(url_for("managercreateItem"))
        elif request.form["button_type"] == "a5":
            return redirect(url_for("managerdeleteItem"))
        elif request.form["button_type"] == "a6":
            return redirect(url_for("managerviewCoupon"))
        elif request.form["button_type"] == "a7":
            return redirect(url_for("managersearchCoupon"))
        elif request.form["button_type"] == "a8":
            return redirect(url_for("managerupdateCoupon"))
        elif request.form["button_type"] == "a9":
            return redirect(url_for("managercreateCoupon"))
        elif request.form["button_type"] == "a10":
            return redirect(url_for("managerdeleteCoupon"))

    def displayItem(self, list) -> list:
        return render_template("managerviewitem.html", query=list)

    def displayItemUpdate(self, list) -> list:
        return render_template("managerupdateitem.html", query=list)

    def displayItemCreate(self, list) -> list:
        return render_template("managercreateitem.html", query=list)

    def displayItemDelete(self, list) -> list:
        return render_template("managerdeleteitem.html", query = list)

    def displayCoupon(self, list) -> list:
        return render_template("managerviewcoupon.html", query=list)

    def displayCouponUpdate(self, list) -> list:
        return render_template("managerupdatecoupon.html", query=list)

    def displayCouponCreate(self, list) -> list:
        return render_template("managercreatecoupon.html", query=list)

    def displayCouponDelete(self, list) -> list:
        return render_template("managerdeletecoupon.html", query = list)



### MANAGER CONTROLLER ###
class ManagerController:
    def __init__(self) -> None:
        self.entity = ItemCouponInventory()

    def getAllItem(self) -> list:
        return self.entity.generateAllItem()
    
    def getSpecificItem(self, name) -> list:
        return self.entity.generateItem(name)
    
    def updateItem(self, id, name, price) -> list:
        return self.entity.updateNewItem(id, name, price)
    
    def createItem(self, name, price) -> list:
        return self.entity.generateNewItem(name, price)

    def removeItem(self, id) -> list:
        return self.entity.deleteItem(id)

    def getAllCoupon(self) -> list:
        return self.entity.generateAllCoupon()

    def getSpecificCoupon(self, name) -> list:
        return self.entity.generateCoupon(name)

    def createCoupon(self, name, valid_from, valid_till, discount) -> list:
        return self.entity.generateNewCoupon(name, valid_from, valid_till, discount)

    def removeCoupon(self, id) -> list:
        return self.entity.deleteCoupon(id)
    
    def updateCoupon(self, name, valid_from, valid_till, discount, id) -> list:
        return self.entity.updateNewCoupon(name, valid_from, valid_till, discount, id)


### MANAGER ENTITY ###
class ItemCouponInventory:
    def __init__(self) -> None:
        pass

    def generateAllItem(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                query = cursor.fetchall()
        return query

    def generateItem(self, name) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM menuitems WHERE upper(name) like '{}%'".format(name))
                    query = cursor.fetchall()
        return query
    
    def updateNewItem(self, id, name, price) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("UPDATE menuitems SET price = '{}', name = '{}' WHERE item_id = {}".format(name, price, id))
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()
        db.commit()
        return query

    def generateNewItem(self, name, price) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("INSERT INTO menuitems (price, name, ordered_count) VALUES (%s, %s, 0)", (name, price))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()
        
        return query

    def deleteItem(self, id) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("DELETE FROM menuitems WHERE item_id = {}".format(id))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()
        return query
        
    def generateAllCoupon(self) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor.fetchall()
        return query

    def generateCoupon(self, name) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon WHERE upper(name) like '{}%'".format(name))
                query = cursor.fetchall()
        return query 

    def generateNewCoupon(self, name, valid_from, valid_till, discount) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                cursor2.execute("INSERT INTO coupon (name, valid_from, valid_till, discount_percent) VALUES (%s, %s, %s, %s)", (name, valid_from, valid_till, discount))
                db.commit()
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor3.fetchall()
        return query
    
    def deleteCoupon(self, id) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("DELETE FROM coupon WHERE coupon_id = {}".format(id))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                    query = cursor3.fetchall()
        return query

    def updateNewCoupon(self, name, valid_from, valid_till, discount, id) -> list:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("UPDATE coupon SET name = '{}', valid_from = '{}', valid_till = '{}', discount_percent = {} WHERE coupon_id = {}".format(name, valid_from, valid_till, discount, id))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                    query = cursor3.fetchall()
        return query
