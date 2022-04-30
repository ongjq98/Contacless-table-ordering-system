### MODULE IMPORTS ###
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime
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
    if request.method == "GET":
        return LoginPage.loginTemplate() # A-B

    elif request.method == "POST":
        controller = LoginPageController(request.form) # B-C
        entity = User(controller) # C-E

        if entity.doesUserExist(): # E
            controller.userExist() # E-C (return true)

            # login success - add username & account_type in session
            session["username"] = controller.username
            session["account_type"] = controller.account_type

            # redirect page to manager, staff, owner or admin
            return LoginPage.redirectPage(entity.account_type) # C-B

        else:
            controller.userNotExist() # E-C (return false)
            flash(controller.username + " login failed!")
            return LoginPage.loginTemplate() # redirect to login page


### LOGOUT (TO APPLY BCE) ###
@app.route("/logOut")
def logOut():
    if "username" in session: # if a username is in session
        username = session["username"]
        session.pop("username")
        flash(f"{username} logged out successfully!")
        return redirect(url_for("index"))

    else:
        flash("Login first before logging out!")
        return redirect(url_for("index"))


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
        return "owner page!"


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
