### MODULE IMPORTS ###
from tkinter import Menu
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime, time
from classes import * # import all classes from classes.py


### POSTGRESQL CONFIG ###
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'


### SESSION CONFIG (password & period) ###
app = Flask(__name__)
app.secret_key = "duck_rice"
app.permanent_session_lifetime = timedelta(minutes=60)


### LOGIN PAGE ###
@app.route("/", methods=["GET", "POST"])
def index():
    boundary = LoginPage()
    if request.method == "GET":
        return boundary.loginTemplate() # A-B

    elif request.method == "POST":
        if boundary.controller.getCredentials(request.form): # B-C, C-E

            # login success - add username & account_type in session
            session["username"] = request.form["username"]
            session["account_type"] = request.form["type"]

            # redirect page to manager, staff, owner or admin
            return LoginPage.redirectPage(session["account_type"]) # C-B

        else:
            flash(request.form["username"] + " login failed!")
            return boundary.loginTemplate() # redirect to login page


### LOGOUT (TO APPLY BCE) ###
@app.route("/logOut")
def logOut():
    boundary = Logout(session)
    session.clear()
    print(session)
    return boundary.logUserOut()
### MANAGER PAGE ###
@app.route("/manager", methods=["GET", "POST"])
def manager():
    boundary = ManagerPage()
    if request.method == "GET":
        if "username" in session:
            return boundary.managerHomePage(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        return boundary.buttonClicked(request.form)


@app.route("/manager/managerviewItem", methods=["GET", "POST"])
def managerviewItem():
    boundary = ManagerPage()
    if request.method == "GET":
        query = boundary.controller.entity.generateAllItem()
        return boundary.displayItem(query)

    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "submit":
            item_name = request.form["itemname"].upper()
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM menuitems WHERE upper(name) like '{}%'".format(item_name))
                    query = cursor.fetchall()
                    print(query)
                return render_template("managerviewitem.html", query=query)

    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "submit":
            item_name = request.form["itemname"].upper()
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM menuitems WHERE upper(name) like '{}%'".format(item_name))
                    query = cursor.fetchall()
                    print(query)
                return render_template("managerviewitem.html", query=query)

@app.route("/manager/managerupdateItem", methods=["GET", "POST"])
def managerupdateItem():
    if request.method == "GET":
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                query = cursor.fetchall()
         return render_template("managerupdateitem.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            item_name = request.form["itemname2"]
            item_price = request.form["itemprice2"]
            item_id = request.form["item2"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("UPDATE menuitems SET name = '{}', price = {} WHERE item_id = {}".format(item_name, item_price, item_id))
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()
            db.commit()
            return render_template("managerupdateitem.html" , query=query)



@app.route("/manager/managercreateItem", methods=["GET", "POST"])
def managercreateItem():
    if request.method == "GET":
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                query = cursor.fetchall()
         return render_template("managercreateitem.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            item_name = request.form["itemname3"]
            item_price = request.form["itemprice3"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("INSERT INTO menuitems (name, price, ordered_count) VALUES (%s, %s, 0)", (item_name, item_price))
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()
            db.commit()
            return render_template("managerviewitem.html" , query=query)




@app.route("/manager/managerdeleteItem", methods=["GET", "POST"])
def managerdeleteItem():
    if request.method == "GET":
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                query = cursor.fetchall()
        return render_template("managerdeleteitem.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            item_id = request.form["item4"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("DELETE FROM menuitems WHERE item_id = {}".format(item_id))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
                    query = cursor3.fetchall()

            return render_template("managerdeleteitem.html",  query=query)



@app.route("/manager/managerviewCoupon", methods=["GET", "POST"])
def managerviewCoupon():
    if request.method == "GET":
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor.fetchall()
                ##print(query)
        return render_template("managerviewcoupon.html", query=query)

    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "submit":
            coupon_name = request.form["couponname"].upper()
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM coupon WHERE upper(name) like '{}%'".format(coupon_name))
                    query = cursor.fetchall()
                    print(query)
            return render_template("managerviewcoupon.html", query=query)


@app.route("/manager/managerupdateCoupon", methods=["GET", "POST"])
def managerupdateCoupon():
    if request.method == "GET":
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor.fetchall()
         return render_template("managerupdatecoupon.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            coupon_id = request.form["couponid4"]
            coupon_name = request.form["couponname4"]
            valid_from = request.form["validfrom4"]
            valid_till = request.form["validtill4"]
            discount_percent = request.form["coupondiscount4"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("UPDATE coupon SET name = '{}', valid_from = '{}', valid_till = '{}', discount_percent = {} WHERE coupon_id = {}".format(coupon_name, valid_from, valid_till, discount_percent, coupon_id))
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                    query = cursor3.fetchall()
            db.commit()
            return render_template("managerupdatecoupon.html" , query=query)



@app.route("/manager/managercreateCoupon", methods=["GET", "POST"])
def managercreateCoupon():
    if request.method == "GET":
         with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor.fetchall()
         return render_template("managercreatecoupon.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            coupon_name = request.form["couponname3"]
            valid_from = request.form["validfrom3"]
            valid_till = request.form["validtill3"]
            discount_percent = request.form["coupondiscount3"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("INSERT INTO coupon (name, valid_from, valid_till, discount_percent) VALUES (%s, %s, %s, %s)", (coupon_name, valid_from, valid_till, discount_percent))
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                    query = cursor3.fetchall()
            db.commit()
            return render_template("managercreatecoupon.html" , query=query)

@app.route("/manager/managerdeleteCoupon", methods=["GET", "POST"])
def managerdeleteCoupon():
    if request.method == "GET":
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                query = cursor.fetchall()
        return render_template("managerdeletecoupon.html" , query=query)
    elif request.method == "POST":
        if request.form["button_type"] == "r1":
            return redirect(url_for("manager"))
        elif request.form["button_type"] == "Submit":
            coupon_id = request.form["couponID4"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor2:
                    cursor2.execute("DELETE FROM coupon WHERE coupon_id = {}".format(coupon_id))
                    db.commit()
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor3:
                    cursor3.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
                    query = cursor3.fetchall()

            return render_template("managerdeletecoupon.html",  query=query)



### STAFF PAGE ###
@app.route("/staff", methods=["GET", "POST"])
def staff():
    boundary = StaffPage()
    if request.method == "GET":
        if "username" in session:
            return boundary.staffTemplate(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        if request.form["button_type"] == "b1":
            return redirect(url_for('viewCart'))


#-----View Cart----#
@app.route("/staff/ViewCart", methods=["GET", "POST"])
def viewCart():
    boundary = StaffPage()
    if request.method == "GET":
        data = boundary.controller.getCart()
        return boundary.staffTemplateViewCart(data)

    elif request.method == "POST":
        if request.form["button_type"] == "button_search":
            search_cart_id = request.form["search_cart_id"]
            data = boundary.controller.searchCart(search_cart_id)
            return redirect(url_for("searchCart", data=data))

        elif request.form["button_type"]=="button_submit":
            get_cart_id = request.form["cart_id"]
            session['cartId'] = get_cart_id
            data = boundary.controller.getOrders(get_cart_id)
            return redirect(url_for('viewOrders',data=data))


#-----Search Cart----#
@app.route("/staff/ViewCart/SearchCart", methods=["GET", "POST"])
def searchCart():
    boundary = StaffPage()
    if request.method == "GET":
        data = request.args.getlist('data')
        return boundary.staffSearchCart(data)

    if request.method == "POST":
        cart_id = request.form["cart_id"]
        session['cartId'] = cart_id
        data = boundary.controller.getOrders(session['cartId'])
        return redirect(url_for('viewOrders',data=data))


#-----View Orders----#
@app.route("/staff/ViewCart/ViewOrders", methods=["GET", "POST"])
def viewOrders():
    boundary = StaffPage()
    if request.method == "GET":
        all_data = request.args.getlist('data')
        # formatting data
        new_data = []
        for i in all_data:
            all_data_array = i[1:-1].split(', ')
            all_data_array[0] = int(all_data_array[0])
            all_data_array[1] = all_data_array[1][1:-1]
            new_data.append(all_data_array)
        session['fororder'] = new_data
        return boundary.staffTemplateViewOrders(new_data)


    # ACTION FOR UPDATE, DELETE, FULFILL, SEARCH
    elif request.method == "POST":
        if request.form["button_type"] == "button_confirm_edit":
            cart_id = session["cartId"]
            order_id = request.form["order_id"]
            item_id = request.form["item_id"]
            item_quantity = request.form["item_quantity"]
            data = boundary.controller.updateOrder(cart_id, order_id, item_id, item_quantity)
            return redirect(url_for('viewOrders', data=data))

        elif request.form["button_type"] == "button_delete":
            order_id = request.form["order_id"]
            data = boundary.controller.deleteOrder(session['cartId'],order_id)
            return redirect(url_for('viewOrders', data=data))

        elif request.form["button_type"] == "button_insert":
            insert_item_id = request.form["insert_item_id"]
            insert_item_quantity = request.form["insert_item_quantity"]
            insert_is_it_fulfilled = request.form.get("insert_is_it_fulfilled")
            data=boundary.controller.insertOrder(session['cartId'], insert_item_id, insert_item_quantity, insert_is_it_fulfilled)
            return redirect(url_for('viewOrders', data=data))

        elif request.form["button_type"] == "button_fulfill":
            order_id = request.form["fulfill_id"]
            data=boundary.controller.toFulfill(session['cartId'], order_id)
            return redirect(url_for('viewOrders',data=data))

        elif request.form["button_type"] == "button_search":
            search_order_id = request.form["search_order_id"]
            data=boundary.controller.searchOrder(session['cartId'], search_order_id)
            return redirect(url_for('searchOrder', data=data))


#-----Search Orders----#
@app.route("/staff/ViewCart/ViewOrders/SearchOrder", methods=["GET", "POST"])
def searchOrder():
    boundary = StaffPage()
    if request.method == "GET":
        data = request.args.getlist('data')
        return boundary.staffSearchOrder(data)

    if request.method == "POST":
        if request.form["button_type"] == "button_confirm_edit":
            order_id = request.form["order_id"]
            item_id = request.form["item_id"]
            item_quantity = request.form["item_quantity"]
            data=boundary.controller.updateOrder(session['cartId'],order_id,item_id,item_quantity)
            return redirect(url_for('viewOrders', data=data))

        if request.form["button_type"] == "button_delete":
            order_id = request.form["order_id"]
            data=boundary.controller.deleteOrder(session['cartId'],order_id)
            return redirect(url_for('viewOrders', data))

        if request.form["button_type"] == "button_fulfill":
            order_id = request.form["fulfill_id"]
            data = boundary.controller.toFulfill(session['cartId'],order_id)
            return redirect(url_for('viewOrders',data=data))

        if request.form["button_type"] == "button_back":
            print("After click back")
            data = boundary.controller.getOrders(session['cartId'])
            return redirect(url_for('viewOrders', data=data))

###end of staff###





### OWNER PAGE (TO DO) ###
@app.route("/owner", methods=["GET", "POST"])
def owner():
    boundary = OwnerPage()
    if request.method == "GET":
        if "username" in session:
            return boundary.ownerHomePage(session["username"])
        else:
            flash("login first!")
            return redirect(url_for("index"))

    elif request.method == "POST":
        return boundary.buttonClicked(request.form)


#-----Owner functions----#
@app.route("/owner/HourlyAvgSpending", methods=["GET", "POST"])
def display_H_avg_spend():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    else:
        date_request = request.form["calendar"]
        data = boundary.controller.getHourlySpending(date_request)
        #print(data)
        return boundary.displayHourlySpendingReport(date_request, data)




@app.route("/owner/DailyAvgSpending", methods=["GET", "POST"])
def display_D_avg_spend():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    else:
        date_request = request.form["calendar"]
        date_split = date_request.split('-')
        year = int(date_split[0])
        month = int(date_split[1])
        day = int(date_split[2])


        start = datetime(year, month, day, 12, 0, 0)
        end = start + timedelta(hours=6)
        data = boundary.controller.getDailySpending(start, end)
        #print(data)
        dates = []
        for i in range(7):
            temp = str(start).split(" ")[0]
            dates.append(temp)
            start = start - timedelta(days =1)

        #print(dates)
        to_read = zip(dates,data)
        return boundary.displayDailySpendingReport(date_request, to_read)



@app.route("/owner/WeeklyAvgSpending", methods=["GET", "POST"])
def display_W_avg_spend():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getWeeklyDatePage()

    else:
        week_requested = request.form["calendar"] # "2022-W18"
        year = int(week_requested.split("-")[0])
        week = int(week_requested.split("W")[1])

        start_of_week = datetime(year,1,3,12,0,0) + timedelta(weeks=week-1)
        end_of_week = start_of_week + timedelta(days= 6)

        start_date = str(start_of_week).split(" ")[0] #2022-05-06
        end_date =  str(end_of_week).split(" ")[0]

        end = start_of_week + timedelta(hours=6)
        data = boundary.controller.getWeeklySpending(start_of_week, end)
        #print(data)
        dates = []
        for i in range(7):
            temp = str(start_of_week).split(" ")[0]
            dates.append(temp)
            start_of_week = start_of_week + timedelta(days =1)
        #print(dates)

        totalRev = 0
        totalCust = 0
        for row in range(len(data)):
            totalRev += data[row][0]
            totalCust += data[row][1]

        to_read = zip(dates, data)
        return boundary.displayWeeklySpendingReport(week_requested, start_date, end_date, to_read, totalRev, totalCust)

@app.route("/owner/HourlyFrequency", methods=["GET", "POST"])
def display_H_frequency():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    elif request.method == "POST":
        date_request = request.form["calendar"]
        date_split = date_request.split('-')
        year = int(date_split[0])
        month = int(date_split[1])
        day = int(date_split[2])

        data = boundary.controller.getHourlyFrequency(year,month,day)
        return boundary.displayHourlyFrequencyReport(date_request, data)

@app.route("/owner/DailyFrequency", methods=["GET", "POST"])
def display_D_frequency():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    elif request.method == "POST":
        date_request = request.form["calendar"]
        date_split = date_request.split('-')
        year = int(date_split[0])
        month = int(date_split[1])
        day = int(date_split[2])

        #print(month)
        start = datetime(year, month, day, 12, 0, 0)
        end = start + timedelta(hours=6)
        data = boundary.controller.getDailyFrequency(start, end)

        dates = []
        for i in range(7):
            temp = str(start).split(" ")[0]
            dates.append(temp)
            start = start - timedelta(days =1)

        to_read = zip(dates, data)
        return boundary.displayDailyFrequencyReport(date_request, to_read)

@app.route("/owner/WeeklyFrequency", methods=["GET", "POST"])
def display_W_frequency():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getWeeklyDatePage()

    else:
        week_requested = request.form["calendar"] # "2022-W18"
        year = int(week_requested.split("-")[0])
        week = int(week_requested.split("W")[1])

        start_of_week = datetime(year,1,3,0,0,0) + timedelta(weeks=week-1) #2022-05-06 00:00:00
        end_of_week = start_of_week + timedelta(days= 6, hours= 23, minutes=59, seconds=59)

        #print(start_of_week)
        #print(end_of_week)

        start_date = str(start_of_week).split(" ")[0] #2022-05-06
        end_date =  str(end_of_week).split(" ")[0]
        #print(start_date)

        date_split = start_date.split('-')
        year = int(date_split[0])
        month = int(date_split[1])
        day = int(date_split[2])
        start = datetime(year, month, day, 12, 0, 0)
        end = start + timedelta(hours=6)



        data = boundary.controller.getWeeklyFrequency(start,end)
        total = 0
        for row in range(len(data)):
            total += data[row][0]
        #print(data)

        dates = []
        for i in range(7):
            temp = str(start_of_week).split(" ")[0]
            dates.append(temp)
            start_of_week = start_of_week - timedelta(days =1)


        to_read = zip(dates, data)

        return boundary.displayWeeklyFrequencyReport(week_requested,start_date,end_date,to_read,total)

@app.route("/owner/HourlyPreference", methods=["GET", "POST"])
def display_H_preference():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    elif request.method == "POST":
        ddmmyy = request.form["calendar"] # "2022-05-30"

        # convert "2022-05-30" to datetime object
        ddmmyy = ddmmyy.split("-") # ['2022', '05', '30']
        year = int(ddmmyy[0]) # 2022
        month = int(ddmmyy[1]) # 05
        day = int(ddmmyy[2]) # 30

        list = boundary.controller.getHourlyPreference(year, month, day)
        return boundary.displayHourlyPreferenceReport(year, month, day, list)


@app.route("/owner/DailyPreference", methods=["GET", "POST"])
def display_D_preference():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getDatePage()

    elif request.method == "POST":
        ddmmyy = request.form["calendar"] # "2022-05-30"
        ddmmyy = ddmmyy.split("-") # ['2022', '05', '30']
        year = int(ddmmyy[0]) # 2022
        month = int(ddmmyy[1]) # 05
        day = int(ddmmyy[2]) # 30

        list = boundary.controller.getDailyPreference(year, month, day)
        return boundary.displayDailyPreferenceReport(year, month, day, list)



@app.route("/owner/WeeklyPreference", methods=["GET", "POST"])
def display_W_preference():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.getWeeklyDatePage()

    elif request.method == "POST":
        ddmmyy = request.form["calendar"] # "2022-W18"
        year = int(ddmmyy.split("-")[0])
        week = int(ddmmyy.split("W")[1])

        start_of_week = datetime(year,1,3,0,0,0) + timedelta(weeks=week-1)
        end_of_week = start_of_week + timedelta(weeks=1)

        string_start = str(start_of_week).split(" ")[0]
        string_end = str(end_of_week).split(" ")[0]

        list = boundary.controller.getWeeklyPreference(year, week)
        return boundary.displayWeeklyPreferenceReport(week, year, string_start, string_end, list)

        #result = weeklyFoodPreference(year, week)
        #return render_template("WeeklyPreferenceResult.html", week=week, year=year, start=string_start, end=string_end, result=result)



def dailyFoodPreference(year:int, month:int, day:int) -> list:
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


def weeklyFoodPreference(year:int, week:int) -> list:
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

#----End of Owner----#

### ADMIN PAGE (TO DO) ###
@app.route("/admin", methods=["GET", "POST"])
def admin():
    boundary = AdminPage()
    if request.method == "GET":
        if "username" in session:
            return boundary.adminTemplate(session["username"])
    # if request.method == "GET":
    #     return boundary.adminTemplate()
    elif request.method == "POST":
        if request.form["button_type"] == "create_Profile":
            return redirect(url_for('CreateProfile'))
        elif request.form["button_type"] == "edit_Profile":
            return redirect(url_for('UpdateProfile'))
        elif request.form["button_type"] == "view_Profile":
            return redirect(url_for('ViewProfile'))
        elif request.form["button_type"] == "search_Profile":
            return redirect(url_for('SearchProfile'))
        elif request.form["button_type"] == "suspend_Profile":
            return redirect(url_for('SuspendProfile'))
        elif request.form["button_type"] == "create_Account":
            return redirect(url_for('CreateAccount'))
        elif request.form["button_type"] == "edit_Account":
            return redirect(url_for('EditAccount'))
        elif request.form["button_type"] == "view_Account":
            return redirect(url_for('ViewAccount'))
        elif request.form["button_type"] == "search_Account":
            return redirect(url_for('SearchAccount'))
        elif request.form["button_type"] == "suspend_Account":
            return redirect(url_for('SuspendAccount'))

@app.route("/admin/CreateProfile", methods=["GET", "POST"])
def CreateProfile():
    boundary = AdminProfilePage()
    if request.method == "GET":
        return boundary.adminTemplateCreateProfile()
    elif request.method == "POST":
        if boundary.controller.createProfileInfo(request.form):
            flash(request.form["profile_name"] + " successfully created!")
            return redirect(url_for('admin'))
        else:
            flash(request.form["profile_name"] + " already exist")
            return redirect(url_for('admin'))

@app.route("/admin/UpdateProfile", methods=["GET", "POST"])
def UpdateProfile():
    boundary = AdminProfilePage()
    if request.method == "GET":
        return boundary.adminTemplateEditProfile()
    elif request.method == "POST":
        if boundary.controller.editProfileInfo(request.form):
            flash(request.form["profile_name"] + " successfully updated!")
            return redirect(url_for('admin'))
        else:
            flash(request.form["profile_name"] + " update fail or profile does not exist!")
            return redirect(url_for('admin'))

@app.route("/admin/ViewProfile", methods=["GET", "POST"])
def ViewProfile():
    boundary = AdminProfilePage()
    if request.method == "GET":
        return boundary.adminTemplateViewProfile()
    elif request.method == "POST":
        data = boundary.controller.viewProfileInfo(request.form)
        return boundary.adminProfileViewResult(data)

@app.route("/admin/SearchProfile", methods=["GET", "POST"])
def SearchProfile():
    boundary = AdminProfilePage()
    if request.method == "GET":
        return boundary.adminTemplateSearchProfile()
    elif request.method == "POST":
        if boundary.controller.searchProfileInfo(request.form):
            data = boundary.controller.getProfileInfo(request.form)
            return boundary.adminProfileSearchResult(data)
        else:
            flash(request.form["profile_name"] + " profile does not exist!")
            return redirect(url_for('admin'))

@app.route("/admin/SuspendProfile", methods=["GET", "POST"])
def SuspendProfile():
    boundary = AdminProfilePage()
    if request.method == "GET":
        return boundary.adminTemplateSuspendProfile()
    elif request.method == "POST":
        if boundary.controller.suspendProfileInfo(request.form):
            flash(request.form["profile_name"] + " successfully suspended!")
            return redirect(url_for('admin'))
        else:
            flash(request.form["profile_name"] + " suspend fail or profile does not exist!")
            return redirect(url_for('admin'))

@app.route("/admin/CreateAccount", methods=["GET", "POST"])
def CreateAccount():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminTemplateCreateAccount()
    elif request.method == "POST":
        if boundary.controller.createAccountInfo(request.form): # B-C, C-E
            flash(request.form["username"] + " successfully created!")
            return redirect(url_for('admin')) # redirect to admin page
        else:
            flash(request.form["username"] + " of type " + request.form["type"] + " already exist!")
            return redirect(url_for('admin')) # redirect to admin page

@app.route("/admin/UpdateAccount", methods=["GET", "POST"])
def EditAccount():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminTemplateEditAccount()
    elif request.method == "POST":
        if boundary.controller.editAccountInfo(request.form): # B-C, C-E
            flash(request.form["username"] + " successfully updated!")
            return redirect(url_for('admin')) # redirect to admin page
        else:
            flash(request.form["username"] + " update failed or does not exist!")
            return redirect(url_for('admin')) # redirect to admin page

@app.route("/admin/ViewAccount", methods=["GET", "POST"])
def ViewAccount():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminTemplateViewAccount()
    elif request.method == "POST":
        data = boundary.controller.viewAccountInfo(request.form)
        return boundary.adminAccountViewResult(data)

@app.route("/admin/SearchAccount", methods=["GET", "POST"])
def SearchAccount():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminTemplateSearchAccount()
    elif request.method == "POST":
        if boundary.controller.searchAccountInfo(request.form): # B-C, C-E #return true if account exist
            data = boundary.controller.getDatabyUInfo(request.form)
            username = [[x[0]] for x in data]
            account_type = [[x[2]] for x in data]
            return boundary.adminAccountSearchResult(username, account_type)
        else:
            flash(request.form["username"] + " account does not exist!")
            return redirect(url_for('admin')) # redirect to admin page

@app.route("/admin/SuspendAccount", methods=["GET", "POST"])
def SuspendAccount():
    boundary = AdminPage()
    if request.method == "GET":
        return boundary.adminTemplateSuspendAccount()
    elif request.method == "POST":
        if boundary.controller.suspendAccountInfo(request.form): # B-C, C-E
            flash(request.form["username"] + " successfully suspended!")
            return redirect(url_for('admin')) # redirect to admin page
        else:
            flash(request.form["username"] + " suspend fail or does not exist!")
            return redirect(url_for('admin')) # redirect to admin page

#----End of Admin----#


### CUSTOMER PAGE (TO DO) ###
@app.route("/customer", methods=["GET", "POST"])
def customer():
    if request.method == "GET":
        return render_template("customer.html")


@app.errorhandler(500)
def page_not_found(e):
    flash("Unauthorized!")
    return redirect(url_for("index"))


### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=False)
