from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re
from datetime import timedelta, date, datetime


# postgresql configs
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'


def login(username, password, account_type) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (username, password, account_type))
                result = cursor.fetchone()
                db.commit()

    if result != None: return True
    else: return False


### MANAGER QUERIES ###
def getAllMenuItems() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
            db.commit()
    return query

def addMenuItem(name, price) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("INSERT INTO menuitems (name, price, ordered_count) VALUES (%s, %s, 0)", (name, price))
            db.commit()

addMenuItem("Ice Lemon Tea", 2.0)

### OWNER QUERIES ###
def getAllUsers() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users;")
            query = cursor.fetchall()
            db.commit()
    return query
