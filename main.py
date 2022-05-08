### MODULE IMPORTS ###
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
    return boundary.logUserOut()



### MANAGER PAGE ###
@app.route("/manager", methods=["GET", "POST"])
def manager():
    if request.method == "GET":
        if session["account_type"] == "manager": # check if manager has logged in before
            return render_template("manager.html", username=session["username"])
        else:
            flash("Login first!")
            return LoginPage.loginTemplate()


### STAFF PAGE (TO DO) ###
@app.route("/staff", methods=["GET", "POST"])
def staff():
    #if request.method == "GET":
    #    return render_template("staff.html")
    boundary = StaffPage()
    if request.method == "GET":
        print("In GET")
        return boundary.staffTemplate() # A-B

#-----View Cart----#
@app.route("/staff/ViewCart", methods=["GET", "POST"])
def viewCart():
    boundary = StaffPage()
    if request.method == "POST":
        print("IN GET FOR viewCart()")
        return render_template("staffViewCart.html", data=boundary.controller.getCart(), cart_id=boundary.controller.getCartId())





### OWNER PAGE (TO DO) ###
@app.route("/owner", methods=["GET", "POST"])
def owner():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.ownerHomePage()

    elif request.method == "POST":
        return boundary.buttonClicked(request.form)


#-----Owner functions----#
@app.route("/owner/HourlyAvgSpending", methods=["GET", "POST"])
def display_H_avg_spend():
    if request.method == "GET":
        return render_template("HourlySpending.html")

    else:
        date_request = request.form["calendar"]
        #get total earnings
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT sum(total_amount) from cart where start_time between '{} 12:00:00' and '{} 17:59:59'".format(date_request))
                totalRevenue = cursor.fetchall()

        #get total Customers
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT count(cart_id) from cart where start_time between '{} 12:00:00' and '{} 17:59:59'".format(date_request))
                totalCustomer = cursor.fetchall()

        result = zip(totalRevenue,totalCustomer)
        return render_template("HourlySpending.html", totalHours=6, totalRevenue=totalRevenue, totalCustomer=totalCustomer, date_request = date_request, result = result)


@app.route("/owner/DailyAvgSpending", methods=["GET", "POST"])
def display_D_avg_spend():
    if request.method == "GET":
        return render_template("DailySpending.html")

    else:
        date_request = request.form["calendar"]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT sum(total_amount) from cart where start_time between '{} 12:00:00' and '{} 17:59:59'".format(date_request))
                totalRevenue = cursor.fetchall()

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT count(cart_id) from cart where start_time between '{} 12:00:00' and '{} 17:59:59'".format(date_request))
                totalCustomer = cursor.fetchall()

        result = zip(totalRevenue,totalCustomer)
        print(totalRevenue)
        print(totalCustomer)
        return render_template("DailySpending.html", totalRevenue=totalRevenue, totalCustomer=totalCustomer, result=result, date_request=date_request)


@app.route("/owner/WeeklyAvgSpending", methods=["GET", "POST"])
def display_W_avg_spend():
    if request.method == "GET":
        return render_template("WeeklySpending.html")
    else:
        ddmmyy = request.form["birthday"] # "2022-W18"
        year = int(ddmmyy.split("-")[0])
        week = int(ddmmyy.split("W")[1])

        start_of_week = datetime(year,1,1,0,0,0) + timedelta(weeks=week)
        end_of_week = start_of_week + timedelta(weeks=1)

        print(start_of_week)
        print(end_of_week)

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT sum(total_amount) FROM cart WHERE start_time between '{}' and '{}'".format(start_of_week, end_of_week))
                    totalRevenue = cursor.fetchall()

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT sum(total_amount) FROM cart WHERE start_time between '{}' and '{}'".format(start_of_week, end_of_week))
                    totalCustomer = cursor.fetchall()

        print(totalRevenue)
        print(totalCustomer)
        return render_template("WeeklySpending.html")

@app.route("/owner/HourlyFrequency", methods=["GET", "POST"])
def display_H_frequency():
    if request.method == "GET":
        return render_template("HourlyFrequency.html")

    elif request.method == "POST":
        operating_hours = range(12,19)
        date_request = request.form["calendar"]
        date_split = date_request.split('-')
        year = int(date_split[0])
        month = int(date_split[1])
        day = int(date_split[2])
        data = []

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                for hour in operating_hours:
                    start = datetime(year, month, day, hour, 0, 0)
                    end = start + timedelta(minutes=60)
                    cursor.execute("SELECT count(cart_id) FROM cart WHERE start_time between '{}' and '{}'".format(start, end))
                    temp = []
                    temp.append(hour * 100)
                    temp.extend(cursor.fetchall()) # temp = [1400, [1]]
                    data.append(temp) #[[1400, [1]], [1500, [2]],...  ]

        print(data)
        return render_template("HourlyFrequency.html", date_request=date_request, data=data)


@app.route("/owner/HourlyPreference", methods=["GET", "POST"])
def display_H_preference():
    if request.method == "GET":
        return render_template("HourlyPreference.html")

    elif request.method == "POST":
        ddmmyy = request.form["birthday"] # "2022-05-30"

        # convert "2022-05-30" to datetime object
        ddmmyy = ddmmyy.split("-") # ['2022', '05', '30']
        year = int(ddmmyy[0]) # 2022
        month = int(ddmmyy[1]) # 05
        day = int(ddmmyy[2]) # 30
        start_of_selected_day = datetime(year, month, day, 0, 0, 0)
        end_of_selected_day = datetime(year, month, day, 23, 59, 59)


@app.route("/owner/DailyPreference", methods=["GET", "POST"])
def display_D_preference():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.dailyPreferencePage()

    elif request.method == "POST":
        ddmmyy = request.form["birthday"] # "2022-05-30"
        ddmmyy = ddmmyy.split("-") # ['2022', '05', '30']
        year = int(ddmmyy[0]) # 2022
        month = int(ddmmyy[1]) # 05
        day = int(ddmmyy[2]) # 30

        result = dailyFoodPreference(year, month, day)
        return render_template("DailyPreferenceResult.html", year=year, month=month, day=day, result=result)



@app.route("/owner/WeeklyPreference", methods=["GET", "POST"])
def display_W_preference():
    boundary = OwnerPage()
    if request.method == "GET":
        return boundary.weeklyPreferencePage()

    elif request.method == "POST":
        ddmmyy = request.form["birthday"] # "2022-W18"
        year = int(ddmmyy.split("-")[0])
        week = int(ddmmyy.split("W")[1])

        start_of_week = datetime(year,1,3,0,0,0) + timedelta(weeks=week)
        end_of_week = start_of_week + timedelta(weeks=1)

        string_start = str(start_of_week).split(" ")[0]
        string_end = str(end_of_week).split(" ")[0]

        result = weeklyFoodPreference(year, week)

        return render_template("WeeklyPreferenceResult.html", week=week, year=year, start=string_start, end=string_end, result=result)



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
    if request.method == "GET":
        return render_template("admin.html")
    else:
        if request.form["button_type"] == "create_Account":
            return render_template("adminCA.html")
#    boundary = AdminPage()
#    if request.method == "GET":
#        return boundary.adminTemplate() # A-B
#    else:
#        if request.form["button_type"] == "viewCart":
#            return redirect(url_for("viewCart"))




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
