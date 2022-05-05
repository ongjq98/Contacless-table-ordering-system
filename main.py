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
        print("IN POST viewCart()")
        table_id = request.form["tableid"]
        return render_template("staffViewCart.html", data=boundary.controller.entity.getCartDetails(table_id))



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
        elif request.form["button_type"] == "b7":
            return redirect(url_for("display_H_preference"))


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



         return render_template("HourlyPreference.html")

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
