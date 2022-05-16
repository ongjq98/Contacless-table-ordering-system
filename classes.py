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
                cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (self.username, self.password, self.account_type))
                result = cursor.fetchone()
                db.commit()

                if result != None: return True
                else: return False


    def createAccount(self) -> _void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"INSERT INTO users (profile, username, password, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (self.account_type, self.username, self.password, self.grant_view_statistics, self.grant_view_edit_cart, self.grant_view_edit_accounts, self.grant_view_edit_menu, self.grant_view_edit_coupon))
                db.commit()

    def editAccount(self) -> _void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"UPDATE users SET username=%s, password=%s, profile=%s WHERE username=%s AND profile=%s", (self.new_username, self.new_password, self.new_account_type, self.username, self.account_type))
                db.commit()

    def searchAccount(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def fetchResult(self) -> bool:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT username, password, profile FROM users WHERE username='{self.username}'")
                result = cursor.fetchone()
                db.commit()
                if result != None:
                    return True
                else:
                    return False

    def suspendAccount(self) -> _void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"DELETE FROM users WHERE username=%s AND profile=%s", (self.username, self.account_type))
                db.commit()



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
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT profile_name FROM profile")
                profiles = cursor.fetchall()
        return render_template("adminCreateA.html", profiles=profiles)

    def adminTemplateUpdateAccount(self):
        return render_template("adminEditA.html")

    def adminTemplateViewSearchAccount(self):
        return render_template("adminViewSearchA.html")

    def adminTemplateViewAccount(self, username, password, account_type):
        return render_template("adminViewA.html", username=username, password=password, account_type=account_type)

    def adminTemplateSearchAccount(self):
        return render_template("adminSearchA.html")

    def adminTemplateSearchResult(self, username, account_type):
        return render_template("adminSearchResult.html", username=username, account_type=account_type)

    def adminTemplateSuspendAccount(self):
        return render_template("adminSuspendA.html")

class AdminPageController:
    def __init__(self) -> None:
        self.entity = UserAccount()

    def createAccountInfo(self, request_form) -> _void:
        self.entity.username = request_form["username"]
        self.entity.password = request_form["password"]
        self.entity.account_type = request_form["type"]
        #to remove grant view function...
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
        return self.entity.createAccount()

    def editAccountInfo(self, request_form) -> _void:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]

        self.entity.new_username = request_form["NewUsername"]
        self.entity.new_password = request_form["NewPassword"]
        self.entity.new_account_type = request_form["Newtype"]
        return self.entity.editAccount()

    def getSearchInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.searchAccount()

    def searchAccountInfo(self, request_form) -> bool:
        self.entity.username = request_form["username"]
        return self.entity.fetchResult()

    def suspendAccountInfo(self, request_form) -> _void:
        self.entity.username = request_form["username"]
        self.entity.account_type = request_form["type"]
        return self.entity.suspendAccount()

### STAFF Use case ###
class StaffPage:
    def __init__(self) -> None:
        self.controller = StaffPageController()
        self.doesCartExist = False

    def staffTemplate(self):
        return render_template("staff.html")

    def staffTemplateViewCart(self):
        return str("staffViewCart.html")

    def staffTemplateViewOrders(self):
        return str("staffViewOrders.html")

    def staffTemplateFulfillOrders(self):
        return str("staffFulfillOrders.html")


class StaffPageController:
    def __init__(self) -> None:
        self.entity = CartDetails()

    def getCart(self) -> bool:
        #self.entity.table_id=request_form["table_id"]
        return self.entity.doesCartExist()


    def getOrders(self,cart_id) -> None:
        print("Inside getOrders")
        return self.entity.retrieveOrders(cart_id)

    def updateOrder(self,current_cart_id, order_id,item_name,quantity) -> None:
        return self.entity.updateOrder(current_cart_id,order_id,item_name,quantity)

    def deleteOrder(self,current_cart_id, order_id) ->None:
        return self.entity.deleteOrder(current_cart_id,order_id)

    def insertOrder(self,current_cart_id, item_id,item_name,item_quantity,item_price,is_it_fulfilled) ->None:
        print("in controller for insertOrder")
        return self.entity.insertOrder(current_cart_id, item_id,item_name,item_quantity,item_price,is_it_fulfilled)

    def toFulfill(self,curret_cart_id,order_id) -> None:
        return self.entity.fulfillOrder(curret_cart_id, order_id)



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
        cursor.execute(f"SELECT * FROM public.""cart"" where is_it_paid=false; ")
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
                cursor.execute(f"SELECT order_id, name, quantity, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (cart_id, ))
                result = cursor.fetchall()
                db.commit()

                print("Inside retrieveOrders")

                if result != None:
                    print ("cart exists")

                    return result
                else: return False

    def updateOrder(self,current_cart_id,order_id,name,quantity)-> _void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"UPDATE public.""order"" SET name = %s, quantity = %s WHERE order_id = %s;", (name, quantity, order_id, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price,is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                #result = cursor.fetchall()

                if result != None:
                   return result
                else: return False


    def deleteOrder(self,current_cart_id,order_id)->_void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"DELETE FROM public.""order"" WHERE order_id = %s;", (order_id, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price,is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                if result != None:
                   return result
                else: return False

    def insertOrder(self,current_cart_id, item_id,item_name,item_quantity,item_price,is_it_fulfilled)->_void:
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                dt = datetime.now()
                cursor.execute(f"INSERT INTO public.""order""(item_id, cart_id, name, quantity, price, ordered_time, is_it_fulfilled) VALUES (%s, %s, %s, %s, %s, %s, %s);",(item_id,current_cart_id,item_name,item_quantity,item_price,dt,is_it_fulfilled, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                if result != None:
                   return result
                else: return False

    def fulfillOrder(self,current_cart_id,order_id) -> _void:
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:#is_it_paid will change to false when submitting!
                cursor.execute(f"UPDATE public.""order"" SET is_it_fulfilled = true WHERE order_id = %s;", (order_id, ))
                db.commit()
                cursor.execute(f"SELECT order_id, name, quantity, price, is_it_fulfilled FROM public.""order"" WHERE cart_id = %s;", (current_cart_id, ))
                db.commit()
                result = cursor.fetchall()
                print("in fulfill order in class.py")
                if result != None:
                   return result
                else: return False

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
                start_of_week = datetime(year,1,3,0,0,0) + timedelta(weeks=week)
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