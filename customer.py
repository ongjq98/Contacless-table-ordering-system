########customer.py###########
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
        if session.get("cartId","") == "": #session not exist yet
             return boundary.customerHomePage()
        else:
            
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
        if request.form.get("searchclick","") == "searchclick":
            session["query"] = request.form["query"]
            return redirect(url_for("add_orderSearchMenu"))
        if request.form.get("return", "") == "return":
            print("return pressed")
            return redirect(url_for("index"))

        elif ("return" not in request.form and "searchclick" not in request.form):
            print("ADD ORDER FORM submitted")
            orderlist =  boundary.controller.getOrderlistToAdd(request.form, request.form.getlist)
            print(orderlist)
            print(boundary.controller.entity.cart_id)
            return boundary.redirectToCustomerPage(orderlist)
    
            
       
### CUSTOMER ADD ORDER SEARCH MENU ###
@app.route("/add_orderSearchMenu", methods=["GET", "POST"])
def add_orderSearchMenu():
    boundary = CustomerPage()
    if request.method == "GET":
        print("Customer Add Order Page")
        
        boundary_menu =  CustomerPage()
        menu = boundary_menu.controller.getSearchQuery()
        return boundary.addOrderPage(menu) 

    elif request.method == "POST":
        if request.form.get("searchclick","") == "searchclick":
            session["query"] = request.form["query"]
            return redirect(url_for("add_orderSearchMenu"))
        if request.form.get("return", "") == "return":
            print("return pressed")
            return redirect(url_for("index"))

        elif ("return" not in request.form and "searchclick" not in request.form):
            print("ADD ORDER FORM submitted")
            orderlist =  boundary.controller.getOrderlistToAdd(request.form, request.form.getlist)
            print(orderlist)
            print(boundary.controller.entity.cart_id)
            return boundary.redirectToCustomerPage(orderlist)         
        

### EDIT PAGE ###
@app.route("/editOrder", methods=["GET", "POST"])
def editOrder():  
    boundary2 = CustomerPage()
    if request.method == "GET":
        print("Edit ORDER")
        #Menu Boundary
        boundary_menu =  CustomerPage()
        menu = boundary_menu.controller.getMenu()

        #CurrentOrders Boundary
        currentOrders_boundary = CustomerPage()
        currentOrders = currentOrders_boundary.controller.getCurrentOrders()
        return boundary2.editOrderPage(menu, currentOrders) 

    elif request.method == "POST":
        if request.form.get("searchclick","") == "searchclick":
            session["query"] = request.form["query"]
            return redirect(url_for("add_orderSearchMenu"))
        if request.form.get("return", "") == "return":
            print("return pressed")
            return redirect(url_for("index"))

        elif ("return" not in request.form and "searchclick" not in request.form):
            boundary2.controller.entity.cart_id = session["cartId"]
            boundary2.controller.entity.table_id = session["tableId"]
            boundary2.controller.entity.phone_no = session["phone_no"]
            orderlist =  boundary2.controller.getOrderlistToUpdateAndAdd(request.form, request.form.getlist)
            return boundary2.redirectToCustomerPage(orderlist)

### EDIT PAGE Search menu ###
@app.route("/editOrderSearchMenu", methods=["GET", "POST"])
def editOrderSearchMenu():  
    boundary2 = CustomerPage()
    if request.method == "GET":
        print("Edit ORDER")
        #Menu Boundary
        boundary_menu =  CustomerPage()
        menu = menu = boundary_menu.controller.getSearchQuery()

        #CurrentOrders Boundary
        currentOrders_boundary = CustomerPage()
        currentOrders = currentOrders_boundary.controller.getCurrentOrders()
        return boundary2.editOrderPage(menu, currentOrders) 

    elif request.method == "POST":
        if "return" not in request.form:
            boundary2.controller.entity.cart_id = session["cartId"]
            boundary2.controller.entity.table_id = session["tableId"]
            boundary2.controller.entity.phone_no = session["phone_no"]
            orderlist =  boundary2.controller.getOrderlistToUpdateAndAdd(request.form, request.form.getlist)
            return boundary2.redirectToCustomerPage(orderlist)
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
        #CurrentOrders Boundary
        currentOrders_boundary = CustomerPage()
        currentOrders = currentOrders_boundary.controller.getCurrentOrders()
        return boundary3.deleteOrderPage(currentOrders) # A-B 

    elif request.method == "POST":
        if "return" not in request.form:
            boundary3.controller.entity.cart_id = session["cartId"]
            boundary3.controller.entity.table_id = session["tableId"]
            boundary3.controller.entity.phone_no = session["phone_no"]
            orderlist = boundary3.controller.getOrderlistToDelete(request.form.getlist)
            return boundary3.redirectToCustomerPage(orderlist)
        else:
            if request.form["return"] == "return":
                print("return pressed")
                return redirect(url_for("index"))
                
### PAYMENT ORDER PAGE ###
@app.route("/payment", methods=["GET", "POST"])
def payment():  
    boundary4 = CustomerPage()
    if request.method == "GET":
        #CurrentOrders Boundary
        currentOrders_boundary = CustomerPage()
        currentOrders = currentOrders_boundary.controller.getCurrentOrders()
        print("PAYMENT ORDER")
        return boundary4.payment(currentOrders) # A-B 

    elif request.method == "POST":
        if "return" not in request.form:
            boundary4.controller.entity.cart_id = session["cartId"]
            boundary4.controller.entity.table_id = session["tableId"]
            boundary4.controller.entity.phone_no = session["phone_no"]
            if boundary4.controller.getpaymentDetails(request.form):
                flash("Payment Successful!")
                return boundary4.redirectToCustomerPage([])
            else:
               
                currentOrders_boundary = CustomerPage()
                currentOrders = currentOrders_boundary.controller.getCurrentOrders()
                flash(session["error"])
                return boundary4.redirectToCustomerPage(currentOrders)
        
        else:
            if request.form["return"] == "return":
                print("return pressed")
                return redirect(url_for("index"))

        

        

### VIEW Menu ###
@app.route("/viewMenu", methods=["GET", "POST"])
def viewMenu():
    pass



### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True)

