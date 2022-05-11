### IMPORTS ###
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


### Use Case 1 (LOGIN) ###
class LoginPage:
    def __init__(self) -> None:
        self.controller = LoginPageController()
        self.user_exist = False

    def loginTemplate(self):
        return render_template("login.html")

    def redirectPage(account_type):
        return redirect(url_for(account_type))


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


class UserAccount:
    def doesUserExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.checkDatabase(cursor, db)

    def checkDatabase(self, cursor, db) -> bool:
        # check db - does user exist
        cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (self.username, self.password, self.account_type))
        result = cursor.fetchone()
        db.commit()

        if result != None: return True
        else: return False

    def doesAccountCreateSuccess(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.createAccount(cursor, db)

    def createAccount(self, cursor, db) -> bool:
        cursor.execute(f"INSERT INTO users (profile, username, password, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (self.account_type, self.username, self.password, self.grant_view_statistics, self.grant_view_edit_cart, self.grant_view_edit_accounts, self.grant_view_edit_menu, self.grant_view_edit_coupon))
        db.commit()
        return True
    
    def doesAccountEditSuccess(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.editAccount(cursor, db)

    def editAccount(self, cursor, db) -> bool:
        cursor.execute(f"UPDATE users SET username=%s, password=%s, profile=%s WHERE username=%s AND profile=%s", (self.new_username, self.new_password, self.new_account_type, self.username, self.account_type))
        db.commit()
        return True
    
    def searchAccountSuccess(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.searchAccount(cursor, db)
    
    def searchAccount(self, cursor, db) -> _void:
        cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
        result = cursor.fetchall()
        db.commit()
        if result != None: 
            return result
        else: 
            return False
    
    def doesAccountSuspendSuccess(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.suspendAccount(cursor, db)

    def suspendAccount(self, cursor, db) -> bool:
        cursor.execute(f"DELETE FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
        db.commit()
        return True
    
    #def searchData(self, username) -> bool:
     #   with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
      #      with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
       #         return self.getAllData(cursor, db, username)

    #def getAllData(self, cursor, db, username) -> _void:
     #   cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s", (username))
      #  result = cursor.fetchall()
       # db.commit()
        #if result != None: 
         #   return result
        #else: 
         #   return False

### Use Case 2 (LOGOUT) ###
class Logout:
    def __init__(self, session) -> None:
        self.session = session
        self.username = session["username"]
        self.controller = LogoutController(self.session, self.username)

    def logUserOut(self):
        self.session = self.controller.editSession(self.session, self.username)
        flash(f"{self.username} logged out!")
        return redirect(url_for("index"))


class LogoutController:
    def __init__(self, session, username) -> None:
        self.session = session
        self.username = session["username"]
        self.entity = UserSession()

    def editSession(self, session, username):
        return self.entity.checkUserInSession(session, username)


class UserSession:
    def checkUserInSession(self, session, username):
        self.session = session
        if "username" in session and session["username"] == username:
            return self.removeUserSession(username)

    def removeUserSession(self, username):
        self.session.pop("username")
        return self.session

### ADMIN Use Case (entity go back to UserAccount)###
class AdminPage:
    def __init__(self) -> None:
        self.controller = AdminPageController()

    def adminTemplate(self):
        return render_template("admin.html")

    def adminTemplateCreateAccount(self):
        return render_template("adminCA.html")

    def adminTemplateSearch(self):
        return render_template("adminSearch.html")

class AdminPageController:
    def __init__(self) -> None:
        self.entity = UserAccount()

    def createAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.password = request_form["password"]
        self.entity.account_type = request_form["type"]

        if request_form["type"] == "manager": 
            self.entity.grant_view_statistics = False
            self.entity.grant_view_edit_cart = False
            self.entity.grant_view_edit_accounts = False
            self.entity.grant_view_edit_menu = True
            self.entity.grant_view_edit_coupon = True
        elif request_form["type"] == "staff": 
            self.entity.grant_view_statistics = False
            self.entity.grant_view_edit_cart = True
            self.entity.grant_view_edit_accounts = False
            self.entity.grant_view_edit_menu = False
            self.entity.grant_view_edit_coupon = False
        elif request_form["type"] == "owner": 
            self.entity.grant_view_statistics = True
            self.entity.grant_view_edit_cart = False
            self.entity.grant_view_edit_accounts = False
            self.entity.grant_view_edit_menu = False
            self.entity.grant_view_edit_coupon = False
        elif request_form["type"] == "admin": 
            self.entity.grant_view_statistics = False
            self.entity.grant_view_edit_cart = False
            self.entity.grant_view_edit_accounts = True
            self.entity.grant_view_edit_menu = False
            self.entity.grant_view_edit_coupon = False
        return self.entity.doesAccountCreateSuccess()

    def editAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]

        self.entity.new_username = request_form["NewUsername"]
        self.entity.new_password = request_form["NewPassword"]
        self.entity.new_account_type = request_form["Newtype"]
        return self.entity.doesAccountEditSuccess()


    def getSearchInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.searchAccountSuccess()

    def suspendAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.doesAccountSuspendSuccess()
    #def getDataInfo(self, username) -> bool:
     #   return self.entity.searchData(username)

### STAFF Use case ###
class StaffPage:
    def __init__(self) -> None:
        self.controller = StaffPageController()
        self.doesCartExist = False

    def staffTemplate(self):
        return render_template("staff.html")

    def staffTemplateViewCart(self):
        return render_template("staffViewCart.html")

    def staffTemplateViewOrders(self):
        return render_template("staffViewOrders.html")


class StaffPageController:
    def __init__(self) -> None:
        self.entity = CartDetails()

    def getCart(self) -> bool:
        #self.entity.table_id=request_form["table_id"]
        return self.entity.doesCartExist()


    def getOrders(self,cart_id) -> None:
        print("Inside getOrders")
        return self.entity.retrieveOrders(cart_id)


    def getCartId(self):
        return self.entity.getCartId()


class CartDetails:
    def doesCartExist(self) -> bool:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.retrieveCart(cursor, db)

    def retrieveCart(self, cursor, db) -> _void:
        # check db - does cart exist
        print("In database area")
        #is_it_paid will change to false when submitting!
        cursor.execute(f"SELECT cart_id,table_id, phone_no, start_time, end_time, total_amount, coupon_discount FROM public.""cart"" where is_it_paid=true; ")
        result = cursor.fetchall()

        db.commit()

        if result != None:
            print ("cart exists")

            return result
            #procees to retrieve by calling retrieveCartDetails
            #return self.retrieveCartDetails(cursor,db,cart_id)
        else: return False

    def retrieveOrders(self,cart_id)-> _void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"SELECT order_id, item_id, cart_id, name, quantity, price, ordered_time, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (cart_id, ))
                result = cursor.fetchall()
                db.commit()

                print("Inside retrieveOrders")

                if result != None:
                    print ("cart exists")

                    return result
                else: return False

    #def getCartId(self) -> _void:
    #    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
    #        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
    #            cursor.execute(f"SELECT cart_id FROM public.""cart"" where is_it_paid=true; ")
    #            result = cursor.fetchall()
    #            db.commit()

    #            if result != None:
    #                return result
            #procees to retrieve by calling retrieveCartDetails
            #return self.retrieveCartDetails(cursor,db,cart_id)
    #            else: return False
    #def retrieveCartDetails(self, cursor, db,cart_id):
    #    print("Inside checkCartDetails1st")
        #SELECT o.name, o.quantity FROM public.""order"" o, cart c WHERE c.cart_id = o.cart_id and c.table_id = %s; ",(table_id, )
    #    cursor.execute(f"SELECT * FROM public.""cart"" WHERE cart_id= %s; ",(cart_id, ))
    #    result = cursor.fetchall()
    #    db.commit()
    #    print("Inside checkCartDetails")
    #    return result

    #def getCartDetails(self,cart_id) -> _void:
    #    print("Inside getCartDetails")
    #    return self.doesCartExist(cart_id)



##customer<1>######

#entiy
class CustomerAddOrderPage:
    def __init__(self) -> None:
        self.controller = CustomerAddOrderPageController()
        self.user_exist = False

    def loginTemplate(self):
        return render_template("add_order.html")

#controller
class CustomerAddOrderPageController:
    def __init__(self) -> None:
        self.entity = Orders()

    def getOrderlist(self, request_one, request_many) -> None:
        #self.entity.cart_id = request_form["cartId"]
        self.entity.phone_no = request_one["phone_no"]
        self.entity.item_id = request_many("item_id[]")
        self.entity.table_id = request_one["table_id"]
        self.entity.item_name = request_many("item_name[]")
        self.entity.item_quantity = request_many("item_quantity[]")
        self.entity.item_price = request_many("item_price[]")

        ##add orders into database
        self.entity.ifCustomerExist()


#entity
class Orders:
    def addOrders(self) -> None:
        # connect to db
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                return self.insertDatabase(cursor, db)

    def ifCustomerExist(self) -> None:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                print(type(self.phone_no))
                print(self.item_id)
                cursor.execute(f"SELECT * FROM customer WHERE phone_no = %s;" , (self.phone_no,))
                result = cursor.fetchone()
                print(result)
                db.commit()

                if result != None:
                    self.incrementVisitAndDate(cursor, db)
                else:
                    self.addCustomer(cursor, db)

                self.addOrders()

    def incrementVisitAndDate(self, cursor, db) -> None:
        dt = datetime.now()
        cursor.execute(f"UPDATE customer SET no_of_visits = no_of_visits + 1 WHERE phone_no = %s" , (self.phone_no,))
        db.commit()
        cursor.execute(f"UPDATE customer SET last_visit = %s WHERE phone_no = %s" , (dt,self.phone_no))
        #result = cursor.fetchone()
        db.commit()

    def addCustomer(self, cursor, db) -> None:
        dt = datetime.now()
        cursor.execute(f"INSERT INTO customer(phone_no, no_of_visits, last_visit) VALUES(%s,%s,%s)", (self.phone_no, 1, dt))
        #result = cursor.fetchone()
        db.commit()

    def insertDatabase(self, cursor, db) -> None:
        # check db - does user exist
        dt = datetime.now()
        cursor.execute(f"INSERT INTO cart(table_id, phone_no, start_time, is_it_paid) VALUES(%s, %s, %s, %s) RETURNING cart_id", (self.table_id, self.phone_no, dt, False))
        db.commit()
        added_cart_id = cursor.fetchone()[0]
        print(self.item_id)
        print(self.item_name)
        print(self.item_quantity)
        print(self.item_price)
        #self.cart_id = added_cart_id
        for i in range(len(self.item_name)):
            total_cost = float((self.item_price)[i][1:])* int((self.item_quantity)[i])

            print(total_cost)
            cursor.execute(f'INSERT INTO public."order"(item_id, cart_id, name, quantity, price) VALUES(%s, %s, %s, %s, %s)', ((self.item_id)[i], added_cart_id, (self.item_name)[i], (self.item_quantity)[i], total_cost))
            #result = cursor.fetchone()
            db.commit()

            #if result != None: return True
            #else: return False


### Owner Use Case 7 (Hourly Preferences) ###
class OwnerPage:
    def __init__(self) -> None:
        self.controller = OwnerPageController()

    def ownerHomePage(self):
        return render_template("owner.html")

    def getDailyDatePage(self):
        return render_template("getDatePage.html")
    
    def getWeeklyDatePage(self):
        return render_template("getWeeklyDatePage.html")

    def hourlyPreferencePage(self):
        return render_template("HourlyPreference.html")

    def dailyPreferencePage(self):
        return render_template("DailyPreference.html")

    def weeklyPreferencePage(self):
        return render_template("WeeklyPreference.html")

    def buttonClicked(self, request_form):
        self.button_id = request_form["button_type"]
        template = self.controller.serveSelectedPage(self.button_id)
        return template

    def preferenceResultPage(self, year, month, day, list):
        return render_template("HourlyPreferenceResult.html", year=year, month=month, day=day, hourly_preference_list=list)


class OwnerPageController:
    def __init__(self) -> None:
        self.entity = OwnerOrders()

    def serveSelectedPage(self, button_id):
        if request.form["button_type"] == "b1":
            return redirect(url_for("display_H_avg_spend"))
        elif request.form["button_type"] == "b2":
            return redirect(url_for("display_D_avg_spend"))
        elif request.form["button_type"] == "b3":
            return redirect(url_for("display_W_avg_spend"))
        elif request.form["button_type"] == "b4":
            return redirect(url_for("display_H_frequency"))
        elif request.form["button_type"] == "b5":
            return redirect(url_for("display_D_frequency"))
        elif request.form["button_type"] == "b6":
            return redirect(url_for("display_W_frequency"))
        elif request.form["button_type"] == "b7":
            return redirect(url_for("display_H_preference"))
        elif request.form["button_type"] == "b8":
            return redirect(url_for("display_D_preference"))
        elif request.form["button_type"] == "b9":
            return redirect(url_for("display_W_preference"))

    def getHourlyPreferenceData(self, year, month, day) -> list:
        return self.entity.ordersHourlyPreference(year, month, day)


class OwnerOrders:
    def ordersHourlyPreference(self, year, month, day) -> list:
        operating_hours = range(12,19)
        hourly_preference_list = []

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for hour in operating_hours:
                    start = datetime(year, month, day, hour, 0, 0)
                    end = start + timedelta(minutes=60)
                    name_quantity = self.nameQuantityFromOrders(db, cursor, start, end)

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


    def nameQuantityFromOrders(self, db, cursor, start, end):
        cursor.execute("SELECT name, quantity FROM public.\"order\" WHERE ordered_time between '{}' and '{}'".format(start, end))
        name_quantity = cursor.fetchall() # [['Ice Latte', 4], ['Fish Burger', 1], ...]
        return name_quantity
