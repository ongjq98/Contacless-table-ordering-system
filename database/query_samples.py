# contains postgresql queries in python code for actors to use

from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re, time
from datetime import timedelta, date, datetime

# postgresql configs
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'

### GENERAL ###
def login(username:str, password:str, account_type:str) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
            with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(f"SELECT * FROM users WHERE username = %s AND password = %s AND profile = %s", (username, password, account_type))
                result = cursor.fetchone()
                db.commit()

    if result != None: return True
    else: return False


### MANAGER MENUITEMS ###
def viewAllMenuItems() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
            query = cursor.fetchall()
            db.commit()
    return query


def searchMenuItems(name:str) -> list: # search using name
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM menuitems WHERE name like '{name}%'")
            query = cursor.fetchall()
            db.commit()
    return query


def createMenuItem(name:str, price:float) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("INSERT INTO menuitems (name, price, ordered_count) VALUES (%s, %s, 0)", (name, price))
            db.commit()


def updateMenuItem(id:int, name:str, price:float) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("UPDATE menuitems SET name = '{}', price = {} WHERE item_id = {}".format(name, price, id))
            db.commit()


def deleteMenuItem(id:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("DELETE FROM menuitems WHERE item_id = {}".format(id))
            db.commit()



### MANAGER COUPONS ###
def viewAllCoupons() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM coupon ORDER BY coupon_id ASC")
            query = cursor.fetchall()
            db.commit()
    return query


def searchCoupon(name:str) -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM coupon WHERE name like '{name}%'")
            query = cursor.fetchall()
            db.commit()
    return query


def createCoupon(name:str, valid_from:datetime, valid_till:datetime, discount_percent:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("INSERT INTO coupon (name, valid_from, valid_till, discount_percent) VALUES ('{}', '{}', '{}', {})".format(name, valid_from, valid_till, discount_percent))
            db.commit()

current_datetime = datetime.now()
future_datetime = datetime(2022, 12, 1, 0, 0, 0) # (year, month, day, hour, min, second)
#createCoupon("coupon4", current_datetime, future_datetime, 10)


def updateCoupon(id:int, name:str, valid_from:datetime, valid_till:datetime, discount_percent:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("UPDATE coupon SET name = '{}', valid_from = '{}', valid_till = '{}', discount_percent = '{}' WHERE coupon_id = {}".format(name, valid_from, valid_till, discount_percent, id))
            db.commit()


def deleteCoupon(id:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("DELETE FROM coupon WHERE coupon_id = {}".format(id))
            db.commit()



### CUSTOMER QUERIES ###
def viewAllMenuItems() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM menuitems ORDER BY item_id ASC")
            query = cursor.fetchall()
            db.commit()
    return query


def searchMenuItems(name:str) -> list: # search using name
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM menuitems WHERE name like '{name}%'")
            query = cursor.fetchall()
            db.commit()
    return query


def viewOrders(cart_id:int) -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM public.\"order\" WHERE cart_id = {} ORDER BY order_id ASC".format(cart_id))
            query = cursor.fetchall()
            db.commit()
    return query


def updateOrder(cart_id:int) -> None:
    pass # to ask yongqin how is he going to update order


# after making payment
# -> is_it_paid = True
# -> add end_time = current_datetime
# -> add duration (end_time - start_time) mins
# -> calculate & add total_amount
end_time = datetime.now()
def finishCart(cart_id:int, end_time:datetime, coupon_discount:int) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # find start_time
            try:
                cursor.execute("SELECT start_time FROM cart WHERE cart_id = {}".format(cart_id))
                start_time = cursor.fetchone()[0]

                # find duration in mins
                duration_mins = int((end_time - start_time).total_seconds() / 60)

                # coupon discount, total_amount
                cursor.execute("SELECT total_amount FROM cart where cart_id = {}".format(cart_id))
                query = cursor.fetchone()[0]
                percent_charged = (100 - coupon_discount) / 100
                total_amount = round(query * percent_charged, 2)
                cursor.execute("UPDATE cart SET total_amount = {}, coupon_discount = {} WHERE cart_id = {}".format(total_amount, coupon_discount, cart_id))

                # update end_time, duration, is_it_paid
                cursor.execute("UPDATE cart SET end_time = '{}', duration_mins = {} WHERE cart_id = {}".format(end_time, duration_mins, cart_id))

                # cart is paid
                cursor.execute("UPDATE cart SET is_it_paid = True WHERE cart_id = {}".format(cart_id))
                db.commit()

                return True
            except Exception as e:
                print(e)
                return False

#finishCart(1)

#def createCart(table_id:int, phone_no:int, start_time, end_time)

# to add stack quantity of same item ordered
def createOrder(item_id:int, cart_id:int, name:str, quantity:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("INSERT INTO public.\"order\"(item_id, cart_id, name, quantity) VALUES ({}, {}, '{}', {})".format(item_id, cart_id, name, quantity))
            db.commit()


def deleteOrder(order_id:int) -> None:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("DELETE FROM public.\"order\" WHERE order_id = {}".format(order_id))
            db.commit()


### OWNER QUERIES ###
def getAllStartTime() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT start_time from cart")
            query = cursor.fetchall()
            db.commit()

def getAllUsers() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM users;")
            query = cursor.fetchall()
            db.commit()
    return query

### OWNER ###
# hourly preference for food

def hourlyFoodPreference(start:datetime):
    end = start_time + timedelta(minutes=60)
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # get cart_id(s) that are between start & end time
            cursor.execute("SELECT cart_id from cart WHERE start_time between '{}' and '{}'".format(start, end))
            cart_id_list = cursor.fetchall() # [[43], [47], [40], [74]]

            # get order(quantity, name) from cart_id_list
            name_quantity_dictionary = {} # {"Coke" : 2, ...}
            for cart_id in cart_id_list:
                cursor.execute("SELECT name, quantity from public.\"order\" WHERE cart_id = {}".format(cart_id[0]))
                name_quantity = cursor.fetchall() # [['French Fries', 1], ['Ice Lemon Tea', 1], ['Vege Burger', 5]]
                for pair in name_quantity:
                    item_name = pair[0]
                    item_quantity = pair[1]
                    if item_name in name_quantity_dictionary:
                        name_quantity_dictionary[item_name] += item_quantity
                    else:
                        name_quantity_dictionary[item_name] = item_quantity

            print(name_quantity_dictionary)
            db.commit()


start = datetime(2022, 6, 23, 9, 0, 0)
end = datetime(2022, 6, 23, 10, 0, 0)
#hourlyFoodPreference(start, end)


alpha_dict = {"g": 14, "q": 16, "h": 19}
new_value = max(alpha_dict, key=alpha_dict.get)
print("Highest value from dictionary:",new_value)
