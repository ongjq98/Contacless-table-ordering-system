from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime

app = Flask(__name__)

# postgresql configs
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'

# session configs (password & period)
app.secret_key = "coolstuff"
app.permanent_session_lifetime = timedelta(minutes=60)

# BOTH ADMIN & STUDENT USES session["user"]
# admin sessions has "ADMIN. " in front


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == 'GET':
        if "user" in session: # check if user already logged in
            user = session["user"]
            check = user.split("STAFF." )  # Use split to check if its a admin or student

            if len(check) > 1: # this is a admin
                flash(f"Admin Home Page! Welcome {user} ")
                flash("Please use Nav Bar above to create or view channel")
                return render_template("admin.html", user=user)

            else: # this is a student
                flash(f"{user} already logged in!")
                return render_template("student.html", user=user)

        else: # cannot find any session["user"]
            return render_template("login.html")

    else: # POST method (after user submitted login details)
        user = request.form["username"]
        passwd = request.form["password"]
        type = request.form["type"] # type == "student" or "staff"

        date_list = []
        for days in range(7):
            cur_date = str(date.today() + timedelta(days=int(days)))
            date_list.append(cur_date)
        session["datelist"] = date_list

        if type == "student":
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (user, passwd)) # check db for such user
                    result = cursor.fetchone()
                    db.commit()

            if result != None: # if has a result
                session["user"] = user # make the username to be session["user"]

                # update last_login details
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                    with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute("UPDATE users SET last_login = %s WHERE name = %s AND password = %s", (dt_string, user, passwd))
                        db.commit()

                flash(f"Welcome {user}!")
                return redirect(url_for("student"))
            else: # if no result
                flash(f"Incorrect ID or password for {user}! Try again!")
                return render_template("login.html")

        elif type == "staff": # staff login
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM admins WHERE name = %s AND password = %s", (user, passwd))
                    result = cursor.fetchone()
                    db.commit()

            if result != None: # account is verified

                # update last_login details
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                    with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute("UPDATE admins SET last_login = %s WHERE name = %s AND password = %s", (dt_string, user, passwd))
                        db.commit()

                user = 'STAFF. ' + user # to show its a admin
                session["user"] = user

                return redirect(url_for("admin"))
            else:
                flash(f"Incorrect ID or password for {user}! Try again!")
                return render_template("login.html")

        else: # admin login
            if user == 'Leroy' and passwd == '101adminsys': # since only 1 user, lazy use db
                user = 'ADMIN. ' + user # to show its a admin
                session["user"] = user
                return redirect(url_for("sysadmin"))
            else:
                flash(f"Incorrect ID or password for {user}! Try again!")
                return render_template("login.html")

@app.route("/sysadmin", methods=["POST", "GET"])
def sysadmin():
    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            check = user.split("ADMIN." )

            if len(check) > 1:
                return render_template("sysadmin.html")
            else:
                flash("Login first!")
                return redirect(url_for("index"))

        else:
            flash("Login first!")
            return redirect(url_for("index"))


@app.route("/studentAccounts", methods=["POST", "GET"])
def studentAccounts():
    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            check = user.split("ADMIN." )

            if len(check) > 1:
                with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                    with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM users;")
                        query = cursor.fetchall()
                        db.commit()

                return render_template("studentAccounts.html", query=query)

            else:
                flash("Login first!")
                return redirect(url_for("index"))
        else:
            flash("Login first!")
            return redirect(url_for("index"))

    else:
        name = request.form["delete"]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("DELETE FROM users WHERE name = '{0}';".format(name))
                db.commit()

        flash(f"Deleted student acct : {name}!")
        return render_template("sysadmin.html")


@app.route("/staffAccounts", methods=["POST", "GET"])
def staffAccounts():
    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            check = user.split("ADMIN." )

            if len(check) > 1:
                with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                    with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM admins;")
                        query = cursor.fetchall()
                        db.commit()

                return render_template("staffAccounts.html", query=query)

            else:
                flash("Login First!")
                return redirect(url_for("index"))
        else:
            flash("Login First!")
            return redirect(url_for("index"))


    else:
        name = request.form["delete"]
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("DELETE FROM admins WHERE name = '{0}';".format(name))
                db.commit()

        flash(f"Deleted staff acct : {name}!")
        return render_template("sysadmin.html")


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]

        # check which type of user
        check = user.split("STAFF. " )
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if len(check) > 1:
            user = check[1]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("UPDATE admins SET last_logout = %s WHERE name = %s", (dt_string, user))
                    db.commit()

        else:
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("UPDATE users SET last_logout = %s WHERE name = %s", (dt_string, user))
                    db.commit()

        session.pop("user")
        flash(f"{user} logged out successfully!")
        return redirect(url_for("index"))
    else:
        flash("Need to login first!")
        return redirect(url_for("index"))


@app.route("/signup", methods=["POST", "GET"]) # HTML DOES NOT HAVE LINK TO THIS PAGE
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        user = request.form["username"]
        passwd = request.form["password"]
        email = request.form["email"]
        uow_id = request.form["uow_id"]
        type = request.form["type"]

        if type == "student":
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("INSERT INTO users (name, uow_id, email, password) VALUES (%s, %s, %s, %s)", (user, uow_id, email, passwd))
                    db.commit()
            flash(f"Successfully created user {user}!")
            return redirect(url_for("index"))

        else: # might want to delete
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("INSERT INTO admins (name, uow_id, email, password) VALUES (%s, %s, %s, %s)", (user, uow_id, email, passwd))
                    db.commit()
            flash(f"Successfully created admin {user}!")
            return redirect(url_for("index"))

@app.route("/admin", methods=["POST", "GET"])
def admin():
    date_list = session["datelist"]
    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            check = user.split("STAFF." )

            if len(check) > 1: # admin

                with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                    with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                        cursor.execute("SELECT * FROM channel WHERE creator = '{0}';".format(user))
                        query = cursor.fetchall()
                        db.commit()

                return render_template("admin.html", user=user, query=query)
            else: # student no access to page
                flash(f"Page is only for Staffs!")
                return redirect(url_for("index"))

        else:
            flash(f"Page is only for Staffs!")
            return redirect(url_for("index"))

    else:
        channel_id = request.form["channel_id"]
        session["channel_id"] = channel_id
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT days, capacity, start_date FROM channel WHERE channel_id = '{0}';".format(channel_id))
                query = cursor.fetchone()
                db.commit()

        # query = [3, 3, datetime.date(2020, 10, 20), datetime.date(2020, 10, 23)]
        data = str(query).translate({ord(i): None for i in 'datetime.date()[]\''}).split(", ")

        if len(data[4]) == 1:
            data[4] = '0' + data[4]

        days = data[0]
        capacity = data[1]
        start_date = data[2] + data[3] + data[4]

        return render_template("editchannel.html", days=days, capacity=capacity, start_date=start_date, date_list=date_list, channel_id=channel_id)


@app.route("/deletechannel", methods=["POST"])
def deletechannel():
    channel_id = request.form["channel_id"]
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("DELETE FROM channel WHERE channel_id = '{0}';".format(channel_id))
            db.commit()
    flash(f"Deleted channel {channel_id}!")
    return render_template("index_admin.html")


@app.route("/channel", methods=["POST", "GET"])
def channel():
    global channel_id, date, sess # AVOID UNBOUND LOCAL ERROR FUK
    date = date.today()

    # create a list of next 7 days in date format
    date_list = session["datelist"]

    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            check = user.split("STAFF." )

            if len(check) > 1: # admin
                return render_template("channel.html", date_list=date_list)
            else: # student
                flash(f"Page is only for Staffs!")
                return redirect(url_for("index"))

        else:
            flash(f"Page is only for Staffs!")
            return redirect(url_for("index"))

    else: # POST METHOD
        capacity = request.form["capacity"]
        days = request.form["days"]
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
        end_date = start_date + timedelta(days=int(days))
        description = request.form["description"]
        user = session["user"]
        passcode = request.form["passcode"]
        status = 'Not Launched'

        # inserting into channel table
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("INSERT INTO channel (days, capacity, creator, start_date, end_date, description, passcode, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (days, capacity, user, start_date, end_date, description, passcode, status))
                cursor.execute("SELECT channel_id FROM channel WHERE creator = %s AND start_date = %s AND days = %s", (user, start_date, days))
                channel_id = cursor.fetchone()[0] # channel_id is serial, have to retrieve from channel table
                db.commit()

        # convert from datetime format to string w/o the time
        str_start_date = str(start_date).split(" ")[0]
        str_end_date = str(end_date).split(" ")[0]

        flash(f"Successfully created channel!")
        flash(f"CHANNEL ID : {channel_id}")
        flash(f"CAPACITY : {capacity}")
        flash(f"START DATE : {str_start_date}")
        flash(f"END DATE : {str_end_date}")
        flash(f"CREATED BY : {user}")
        flash(f"DESCRIPTION : {description}")
        flash(f"PASSCODE : {passcode}")
        flash("NOTE: Launch channel at home page for students to start booking!")

        return render_template("index_admin.html", user=user)


@app.route("/viewslots", methods=["POST", "GET"])
def viewslots():
    global date # avoid unbound local error
    date_list = session["datelist"]

    if request.method == "GET":
        if "user" in session:
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM available_slots")
                    query = cursor.fetchall()
                    db.commit()

            return render_template("viewslots.html", query=query, date_list=date_list)

        else:
            flash("Login first!")
            return redirect(url_for("index"))

    else:
        session_time = request.form["session_time"]
        dates = request.form["date"]

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM available_slots WHERE on_date = %s AND session = %s", (dates, session_time))
                query = cursor.fetchall()
                db.commit()

        return render_template("viewslots.html", query=query, date_list=date_list)



@app.route("/student", methods=["POST", "GET"])
def student():
    if request.method == "GET":
        if "user" in session:
            user = session["user"]
            # query for bookings WHERE booker = session["user"]
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM bookings WHERE booker = '{0}';".format(user)) # singular string formatting
                    query = cursor.fetchall()
                    db.commit()

            return render_template("student.html", query=query, user=user)

        else:
            flash("Login first!")
            return redirect(url_for("index"))

    else: # POST method for cancellation of bookings
        cancellation = request.form["cancel"]
        cancellation_data = cancellation.translate({ord(i): None for i in 'datetime.date()\''}).split(", ") # string manipulation

        channel_id = cancellation_data[0]
        session_time = cancellation_data[4]
        capacity = cancellation_data[5]
        date = cancellation_data[1] + cancellation_data[2] + cancellation_data[3]
        user = session["user"]

        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # delete row from bookings
                cursor.execute("DELETE FROM bookings WHERE channel_id = %s AND on_date = %s AND session = %s;", (channel_id, date, session_time))
                # take passcode from channel WHERE channel_id
                cursor.execute("SELECT passcode FROM channel WHERE channel_id = '{0}';".format(channel_id))
                passcode = cursor.fetchone()[0]
                # inserting back to available_slots
                cursor.execute("INSERT INTO available_slots (channel_id, session, on_date, capacity, description, passcode) VALUES (%s, %s, %s, %s, %s, %s)", (channel_id, session_time, date, capacity, 'Someone cancelled this booking', passcode))
                db.commit()


        flash("Cancelled Booking: ")
        flash(f"CHANNEL ID: {channel_id}")
        flash(f"DATE : {date}")
        flash(f"SESSION TIME : {session_time}")
        flash(f"CAPACITY : {capacity}")
        return render_template("index_student.html", user=user)


@app.route("/bookslot", methods=["POST"])
def bookslot():
    date_list = session["datelist"]

    booking = request.form["book"] # list in string format
    booking_data = booking.translate({ord(i): None for i in 'datetime.date()\''}).split(", ") # string manipulation
    passcode = request.form["passcode"]
    booker_capacity = request.form["capacity"]

    # if 'dd' is single digit, add '0' in front
    if len(booking_data[3]) == 1:
        booking_data[3] = '0' + booking_data[3]
        print(booking_data[3])

    channel_id = booking_data[0]
    session_time = booking_data[4]
    capacity = booking_data[5]
    date = booking_data[1] + booking_data[2] + booking_data[3]
    user = session["user"]


    if int(booker_capacity) > int(capacity): # check if booker capacity over the max capacity
        flash(f"{booker_capacity} is more than the max. capacity ({capacity})!")
        # return viewslots.html with filtered setting
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM available_slots WHERE session = %s AND on_date = %s", (session_time, date))
                query = cursor.fetchall()
                db.commit()

        return render_template("viewslots.html", query=query, date_list=date_list, user=user)


    else:
        # authenicate passcode
        with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM available_slots WHERE channel_id = %s AND capacity = %s AND session = %s AND on_date = %s AND passcode = %s", (channel_id, capacity, session_time, date, passcode))
                query = cursor.fetchall()
                db.commit()

        if query != []: # passcode correct
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    # insert into bookings table
                    cursor.execute("INSERT INTO bookings (channel_id, session, booker, on_date, capacity, attendees_no) VALUES (%s, %s, %s, %s, %s, %s)", (channel_id, session_time, user, date, capacity, booker_capacity))
                    # delete row from available_slots table
                    cursor.execute("DELETE FROM available_slots WHERE channel_id = %s AND on_date = %s AND session = %s;", (channel_id, date, session_time))
                    db.commit()

                    flash(f"Successfully booked channel!")
                    flash(f"CHANNEL ID : {channel_id}")
                    flash(f"DATE : {date}")
                    flash(f"SESSION TIME : {session_time}")
                    flash(f"ATTENDEES_NO : {booker_capacity}")
                    flash(f"BOOKED BY : {user}")
                    return render_template("index_student.html", user=user)

        else:
            flash("Incorrect passcode for the session!")

            # return viewslots.html with filtered setting
            with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
                with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM available_slots WHERE session = %s AND on_date = %s", (session_time, date))
                    query = cursor.fetchall()
                    db.commit()

            return render_template("viewslots.html", query=query, date_list=date_list, user=user)



@app.route("/editchannel", methods=["POST"])
def editchannel():
    channel_id = session["channel_id"]
    start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d")
    days = request.form["days"]
    end_date = start_date + timedelta(days=int(days))
    capacity = request.form["capacity"]
    description = request.form["description"]
    passcode = request.form["passcode"]

    # update attributes
    #UPDATE channel SET days = 1, capacity = 1, start_date = '2020-10-10' WHERE channel_id = 35;
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("UPDATE channel SET days = %s, capacity = %s, start_date = %s, end_date = %s, description = %s, passcode = %s WHERE channel_id = %s;", (days, capacity, start_date, end_date, description, passcode, channel_id))

            # delete all from booking & available_slotslot where channel_id = this channel_id
            cursor.execute("DELETE FROM available_slots WHERE channel_id = '{0}';".format(channel_id))
            cursor.execute("DELETE FROM bookings WHERE channel_id = '{0}';".format(channel_id))

            # add new slots to available_slots
            session_times = ["0800 - 1000", "1000 - 1200", "1200 - 1400", "1400 - 1600", "1600 - 1800", "1800 - 2000", "2000 - 2200"]
            for day in range(int(days)):
                s_date = start_date + timedelta(days=int(day))
                for sess in session_times:
                    cursor.execute("INSERT INTO available_slots (channel_id, capacity, session, on_date, description, passcode) VALUES (%s, %s, %s, %s, %s, %s)", (channel_id, capacity, sess, s_date, description, passcode))
            db.commit()

    session.pop("channel_id")
    flash(f"Updated Channel {channel_id}! Click Home to check")
    return render_template("index_admin.html")

@app.route("/launch", methods=["POST"])
def launch():
    channel_id = request.form["channel_id"]
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM channel WHERE channel_id = '{0}';".format(channel_id))
            query = cursor.fetchone()
            capacity = query[2]
            start_date = query[4]
            end_date = query[5]
            description = query[6]
            passcode = query[7]
            days = query[1]

            # after launching of channel, insert into availabile_slots table according to channel details
            session_times = ["0800 - 1000", "1000 - 1200", "1200 - 1400", "1400 - 1600", "1600 - 1800", "1800 - 2000", "2000 - 2200"]
            for day in range(int(days)):
                s_date = start_date + timedelta(days=int(day))
                for sess in session_times:
                    cursor.execute("INSERT INTO available_slots (channel_id, capacity, session, on_date, description, passcode) VALUES (%s, %s, %s, %s, %s, %s)", (channel_id, capacity, sess, s_date, description, passcode))
            cursor.execute("UPDATE channel SET status = 'Launched!' WHERE channel_id = '{0}';".format(channel_id))
            db.commit()
    flash(f"Successfully launched channel!")
    flash(f"CHANNEL ID : {channel_id}")
    flash(f"CAPACITY : {capacity}")
    flash(f"START DATE : {str(start_date)}")
    flash(f"END DATE : {str(end_date)}")
    flash(f"DESCRIPTION : {description}")
    flash(f"PASSCODE : {passcode}")

    return render_template("index_admin.html")

if __name__ == "__main__":
    app.run(debug=True)
