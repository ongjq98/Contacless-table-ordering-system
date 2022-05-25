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


### CUSTOMER HOMEPAGE ###
@app.route("/", methods=["GET", "POST"])
def index():
    boundary = CustomerPage()
    if request.method == "GET":
        print("Customer Home Page")
        return boundary.customerHomePage() # A-B

    elif request.method == "POST":
        print("12345")
        return boundary.buttonClicked(request.form)

### CUSTOMER ADD ORDER ###
@app.route("/add_order", methods=["GET", "POST"])
def add_order():
    boundary = CustomerPage()
    if request.method == "GET":
        print("Customer Add Order Page")
        boundary_menu =  CustomerPage()
        menu = boundary_menu.controller.getMenu()
        return boundary.addOrderPage(menu)

    elif request.method == "POST":
        if "return" not in request.form:
            print("ADD ORDER FORM submitted")
            boundary.controller.getOrderlistToAdd(request.form, request.form.getlist) # B-C, C-E
            session["cartId"] = boundary.controller.entity.cart_id
            session["tableId"] = boundary.controller.entity.table_id
            session["phone_no"] = boundary.controller.entity.phone_no
            return boundary.redirectToCustomerPage()
        else:
            if request.form["return"] == "return":
                print("return pressed")
                return redirect(url_for("index"))




### EDIT PAGE ###
@app.route("/editOrder", methods=["GET", "POST"])
def editOrder():
    boundary2 = CustomerPage()
    if request.method == "GET":
        print("Edit ORDER")
        boundary_menu =  CustomerPage()
        menu = boundary_menu.controller.getMenu()
        return boundary2.editOrderPage(menu)

    elif request.method == "POST":
        if "return" not in request.form:
            boundary2.controller.entity.cart_id = session["cartId"]
            boundary2.controller.entity.table_id = session["tableId"]
            boundary2.controller.entity.phone_no = session["phone_no"]
            boundary2.controller.getOrderlistToUpdateAndAdd(request.form, request.form.getlist)
            return boundary2.redirectToCustomerPage()
        else:
            if request.form["return"] == "return":
                print("return pressed")
                return redirect(url_for("index"))

### DELETE ORDER PAGE ###
@app.route("/deleteOrder", methods=["GET", "POST"])
def deleteOrder():
    boundary3 = CustomerPage()
    if request.method == "GET":
        print("Delete ORDER")
        return boundary3.deleteOrderPage() # A-B

    elif request.method == "POST":
        if "return" not in request.form:
            boundary3.controller.entity.cart_id = session["cartId"]
            boundary3.controller.entity.table_id = session["tableId"]
            boundary3.controller.entity.phone_no = session["phone_no"]
            boundary3.controller.getOrderlistToDelete(request.form.getlist)
            return boundary3.redirectToCustomerPage()
        else:
            if request.form["return"] == "return":
                print("return pressed")
                return redirect(url_for("index"))

### PAYMENT ORDER PAGE ###
@app.route("/payment", methods=["GET", "POST"])
def payment():
    boundary4 = CustomerPage()
    if request.method == "GET":
        print("PAYMENT ORDER")
        return boundary4.deleteOrderPage() # A-B

    elif request.method == "POST":
        boundary4.controller.entity.cart_id = session["cartId"]
        boundary4.controller.entity.table_id = session["tableId"]
        boundary4.controller.entity.phone_no = session["phone_no"]
        boundary4.controller.getpaymentDetails(request.form)
        return boundary4.redirectToCustomerPage()


### VIEW Menu ###
@app.route("/viewMenu", methods=["GET", "POST"])
def viewMenu():
    pass



### INITIALIZATION ###
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
