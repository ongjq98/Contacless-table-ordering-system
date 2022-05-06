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
    if request.method == "GET":
        return render_template("staff.html")


### OWNER PAGE (TO DO) ###
@app.route("/owner", methods=["GET", "POST"])
def owner():
    if request.method == "GET":
        flash(f"hello test")
        return render_template("owner.html",  username="bob")
    else:
        if request.form["button_type"] == "b1":
            return redirect(url_for("display_H_avg_spend"))
        elif request.form["button_type"] == "b4":
            return redirect(url_for("display_H_frequency"))

#-----Owner functions----#
@app.route("/owner/HourlyAvgSpending", methods=["GET", "POST"])
def display_H_avg_spend():
    if request.method == "GET":
        return render_template("HourlySpending.html")
    
    else:
        date_request = request.form["calendar"]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT sum(total_amount) from cart where start_time between '{date_request} 12:00:00' and '{date_request} 17:59:59'")
                totalRevenue = cursor.fetchall()
            db.commit()

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT count(cart_id) from cart where start_time between '{date_request} 12:00:00' and '{date_request} 17:59:59'")
                totalCustomer = cursor.fetchall()
            db.commit()

        print(totalRevenue)
        print(totalCustomer)
        
        tr = [row[0] for row in totalRevenue]
        tc = [row[0] for row in totalCustomer]
        print(tr[0])
        print(tc[0])
        result = avgSpending(6,tr[0],tc[0])
        return render_template("HourlySpending.html", totalHours=6, totalRevenue=totalRevenue, totalCustomer=totalCustomer, date_request = date_request, result = result)

def avgSpending(totalHours, totalRevenue, totalCustomer):
    avg = totalRevenue/totalCustomer/totalHours
    return round(avg,2)






@app.route("/owner/HourlyFrequency", methods=["GET", "POST"])
def display_H_frequency():
    if request.method == "GET":
        return render_template("HourlyFrequency.html")

    elif request.method == "POST":
        data=[
            ("jello", 123)
            ]




        """db= psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host)
        mycursor = db.cursor()
        mycursor.execute("select count(cart_id) from cart where start_time between '2022-05-08 00:00:00' and '2022-05-08 23:59:59' ")
        data = mycursor.fetchall()
        mycursor.execute("select count(cart_id) from cart where start_time between '2022-05-08 00:00:00' and '2022-05-08 23:59:59' ")
        data.extend(mycursor.fetchall()) """
        labels = [row[0] for row in data]
        values =[row[1] for row in data]
        print(values)
        date_request = request.form["calendar"]
        return render_template("HourlyFrequency.html", date_request=date_request,values=values, labels=labels)

#----End of Owner----#





### ADMIN PAGE (TO DO) ###
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        return "admin page!"


### CUSTOMER PAGE (TO DO) ###
@app.route("/customer", methods=["GET", "POST"])
def customer():
    if request.method == "GET":
        return render_template("customer.html")



### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=False)
