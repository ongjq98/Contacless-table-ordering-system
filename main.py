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
        result = avgSpending(35,100,20) 
        return render_template("HourlySpending.html", totalHours=35, totalRevenue=100, totalCustomer=20, avgSpending=result) 

def avgSpending(totalHours, totalRevnue, totalCustomer):
    avg = totalRevnue/totalCustomer/totalHours
    return avg

@app.route("/owner/HourlyFrequency", methods=["GET", "POST"])
def display_H_frequency():
    if request.method == "GET":
        return render_template("HourlyFrequency.html")

    elif request.method == "POST":
         birthday = request.form["birthday"]
         return render_template("HourlyFrequency.html")

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
