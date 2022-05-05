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
    boundary = CustomerAddOrderPage()
    if request.method == "GET":
        return boundary.loginTemplate() # A-B 

    elif request.method == "POST":
        if boundary.controller.getOrderlist(request.form, request.form.getlist): # B-C, C-E

            # login success - add username & account_type in session
            #session["username"] = request.form["username"]
            #session["account_type"] = request.form["type"]

            # redirect page to manager, staff, owner or admin
            #return LoginPage.redirectPage(session["account_type"]) # C-B
            print("managed to insert_data")
        else:
            
            return boundary.loginTemplate() # redirect to login page

    

### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True)

