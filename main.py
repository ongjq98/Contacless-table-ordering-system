### IMPORTS ###
from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime


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
            controller.userExist() # E-C
            return LoginPage.redirectPage(entity.account_type) # C-B

        else:
            controller.userNotExist()
            flash(controller.username + " login failed!")
            return LoginPage.loginTemplate()
            
        

### MANAGER PAGE ###
@app.route("/manager", methods=["GET", "POST"])
def manager():
    if request.method == "GET":
        return "manager page!"


### STAFF PAGE ###
@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "GET":
        return "staff page!"


### OWNER PAGE ###
@app.route("/owner", methods=["GET", "POST"])
def owner():
    if request.method == "GET":
        return "owner page!"


### ADMIN PAGE ###
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        return "admin page!"


### Use Case 1 (LOGIN) ###
class LoginPage:
    def loginTemplate():
        return render_template("login.html")

    def redirectPage(account_type):
        return redirect(url_for(account_type))

    
class LoginPageController:
    def __init__(self, request_form) -> None:
        self.request_form = request_form
        self.user_exist = False
        self.getCredentials()

    def getCredentials(self) -> None:
        self.username = self.request_form["username"]
        self.password = self.request_form["password"]
        self.account_type = self.request_form["type"]

    def userExist(self) -> None:
        self.user_exist = True
    
    def userNotExist(self) -> None:
        self.user_exist = False

class User:
    def __init__(self, LoginPageController) -> None:
        self.username = LoginPageController.username
        self.password = LoginPageController.password
        self.account_type = LoginPageController.account_type

    def doesUserExist(self) -> bool:
        # check db - does admin user exist
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM {self.account_type} WHERE username = %s AND password = %s", (self.username, self.password)) 
                result = cursor.fetchone()
                db.commit()
        
        if result != None: return True
        else: return False

    

    

    

### INITIALIZATION ###
if __name__ == "__main__":
    app.run(debug=True)


