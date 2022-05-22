# contains postgresql insert statements in python code to populate db

from flask import Flask, redirect ,url_for, render_template, request, session, flash
import psycopg2, psycopg2.extras, datetime, re, time, random
from datetime import timedelta, date, datetime

# postgresql configs
db_host = 'ec2-34-193-232-231.compute-1.amazonaws.com'
db_name = 'dcdffat62o43dd'
db_user = 'gahhsnxxsieddf'
db_pw = '5d380f55b8021f5b7a104ef1bd9597c53b921be378f0404dc2104ed883b15576'


### FUNCTIONS ###
def insertAccount(profile:str, username:str, password:str, grant_view_statistics:bool, grant_view_edit_cart:bool, grant_view_edit_accounts:bool, grant_view_edit_menu:bool, grant_view_edit_coupon:bool) -> bool:
     with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            try:
                cursor.execute("INSERT INTO user (profile, username, password, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon) VALUES ({},{},{},{},{},{},{},{})".format(profile, username, password, grant_view_statistics, grant_view_edit_cart, grant_view_edit_accounts, grant_view_edit_menu, grant_view_edit_coupon))
                db.commit()
                return True
            except Exception as e:
                return False


def insertCustomer(phone_no:int, start_time:datetime) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            try:
                cursor.execute("INSERT INTO customer (phone_no, no_of_visits, last_visit) VALUES ({}, 1, '{}')".format(phone_no, start_time))
                db.commit()
                return True
            except Exception as e:
                return False


def addCart(table_id:int, phone_no:int, start_time:datetime) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            try:
                cursor.execute("INSERT INTO cart (table_id, phone_no, start_time, total_amount) VALUES ({}, {}, '{}', 0)".format(table_id, phone_no, start_time))
                db.commit()
                return True
            except Exception as e:
                return False

def getCartID(phone_no:int, start_time:datetime) -> int:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT cart_id FROM cart WHERE phone_no = {} AND start_time = '{}'".format(phone_no, start_time))
            query = cursor.fetchone()
    return query

def randomDatetime(month:int) -> datetime:
    day = random.randint(1,28)
    hour = random.randint(8,22)
    min = random.randint(1,59)
    sec = random.randint(1,59)
    return datetime(2022, month, day, hour, min, sec)


def addOrder(cart_id:int, item_id:int, quantity:int, cart_start_time:datetime) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # find name, price from menuitem
            cursor.execute("SELECT name, price FROM menuitems WHERE item_id = {}".format(item_id))
            query = cursor.fetchone()
            name = query[0]
            price = query[1]
            price = quantity*price

            ordered_time = cart_start_time + timedelta(minutes=random.randint(1,5))

            try:
                # add order
                cursor.execute("INSERT INTO public.\"order\"(item_id, cart_id, name, quantity, price, ordered_time) VALUES ({}, {}, '{}', {}, {}, '{}');".format(item_id, cart_id, name, quantity, price, ordered_time))
                # update cart
                cursor.execute("UPDATE cart SET total_amount = total_amount + {} WHERE cart_id = {}".format(price, cart_id))
                # update menuitem(ordered_count)
                cursor.execute("UPDATE menuitems SET ordered_count = ordered_count + {} WHERE item_id = {}".format(quantity, item_id))
                db.commit()
                return True
            except Exception as e:
                print(e)
                return False


def getCartDetails(cart_id:int) -> float:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT total_amount, end_time, duration_mins from cart WHERE cart_id = {}".format(cart_id))
            query = cursor.fetchone()
    return query


# after making payment
# -> is_it_paid = True
# -> add end_time = current_datetime
# -> add duration (end_time - start_time) mins
# -> calculate & add total_amount
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



### PROCEDURE (new customer) ###
# 1. add new customer to customer table
# 2. add new cart to cart table
# 3. add random orders to cart_id
# 4. finish cart (add end_time, duration, total_amount)
def newCustomerProcedure() -> None:
    phone_no = random.randint(80000000, 99999999)
    start_time = randomDatetime(5)
    table_id = random.randint(1,30)

    # 1. add new customer to customer table
    if insertCustomer(phone_no, start_time): print(f"INSERTED customer of phone no {phone_no}")

    # 2. add new cart to cart table
    if addCart(table_id, phone_no, start_time): print(f"INSERTED cart of customer({phone_no}) on {start_time} at table {table_id}") # add cart
    cart_id = getCartID(phone_no, start_time)[0]

    # 3. add random num of orders to cart_id & update cart
    for x in range(random.randint(3,8)):
        item_id = random.randint(7,21) # item_id only from 7 to 21
        quantity = random.randint(1,5)
        if addOrder(cart_id, item_id, quantity, start_time):
            print(f"added {quantity} x Item ({item_id}) to cart {cart_id}")


    # 4. finish cart (update end_time, duration, total_amount)
    discount_percentages = [0, 10, 20, 30]
    discount_percent = discount_percentages[random.randint(0,3)]
    end_time = start_time + timedelta(minutes=(random.randint(30,120))) # randomize duration of 30 - 120 mins

    if finishCart(cart_id, end_time, discount_percent):
        cart_details = getCartDetails(cart_id)
        total_amount = cart_details[0]
        end_time = cart_details[1]
        duration_mins = cart_details[2]
        print(f"Cart {cart_id}\'s total is {total_amount}, end_time = {end_time}, duration = {duration_mins}")



def getAllCustomerPhone() -> list:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT phone_no from customer")
            query = cursor.fetchall()
    return query



def customerRevisit(phone_no:int, last_visit:datetime) -> bool:
    with psycopg2.connect(dbname=db_name, user=db_user, password=db_pw, host=db_host) as db:
        with db.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            try:
                cursor.execute("UPDATE customer SET no_of_visits = no_of_visits + 1, last_visit = '{}' WHERE phone_no = {}".format(last_visit, phone_no))
                db.commit()
                return True
            except Exception as e:
                print(e)
                return False

### PROCEDURE (existing customer) ###
# 1. update customer's no_of_visit, last_visit
# 2. add new cart to cart table
# 3. add random orders to cart_id
# 4. finish cart (add end_time, duration, total_amount)
def existingCustomerComeback() -> None:
    phone_no = random.choice(customer_phone_list)
    #start_time = randomDatetime(6)
    start_time = datetime(2022, 5, 3, 15, 20, 0)
    table_id = random.randint(1,30)
    # 1. update customer's no_of_visit, last_visit
    if customerRevisit(phone_no, start_time): print(f"customer({phone_no}) revisited at {start_time}")

    # 2. add new cart to cart table
    if addCart(table_id, phone_no, start_time): print(f"INSERTED cart of customer({phone_no}) on {start_time} at table {table_id}") # add cart
    cart_id = getCartID(phone_no, start_time)[0]

    # 3. add random num of orders to cart_id & update cart
    for x in range(random.randint(3,8)):
        item_id = random.randint(7,21) # item_id only from 7 to 21
        quantity = random.randint(1,5)
        if addOrder(cart_id, item_id, quantity, start_time):
            print(f"added {quantity} x Item ({item_id}) to cart {cart_id}")


    # 4. finish cart (update end_time, duration, total_amount)
    discount_percentages = [0, 10, 20, 30]
    discount_percent = discount_percentages[random.randint(0,3)]
    end_time = start_time + timedelta(minutes=(random.randint(30,120))) # randomize duration of 30 - 120 mins

    if finishCart(cart_id, end_time, discount_percent):
        cart_details = getCartDetails(cart_id)
        total_amount = cart_details[0]
        end_time = cart_details[1]
        duration_mins = cart_details[2]
        print(f"Cart {cart_id}\'s total is {total_amount}, end_time = {end_time}, duration = {duration_mins}")


def customOrder() -> None:
    customer_phone_list = [x[0] for x in getAllCustomerPhone()]
    phone_no = random.choice(customer_phone_list)

    start_time = datetime(2022, 5, 4, 12, 20, 0)
    table_id = random.randint(1,30)

    # 1. update customer's no_of_visit, last_visit
    if customerRevisit(phone_no, start_time): print(f"customer({phone_no}) revisited at {start_time}")

    if addCart(table_id, phone_no, start_time): print(f"INSERTED cart of customer({phone_no}) on {start_time} at table {table_id}") # add cart
    cart_id = getCartID(phone_no, start_time)[0]

    item_id = 10 # vege burger
    quantity = 2

    if addOrder(cart_id, item_id, quantity, start_time):
        print(f"added {quantity} x Item ({item_id}) to cart {cart_id}")

    # 4. finish cart (update end_time, duration, total_amount)
    discount_percentages = [0, 10, 20, 30]
    discount_percent = discount_percentages[random.randint(0,3)]
    end_time = start_time + timedelta(minutes=(random.randint(30,120))) # randomize duration of 30 - 120 mins

    if finishCart(cart_id, end_time, discount_percent):
        cart_details = getCartDetails(cart_id)
        total_amount = cart_details[0]
        end_time = cart_details[1]
        duration_mins = cart_details[2]
        print(f"Cart {cart_id}\'s total is {total_amount}, end_time = {end_time}, duration = {duration_mins}")

"""
for i in range(8):
    print(f"----------------------  CUSTOMER {i} FIRST VISIT -----------------------")
    newCustomerProcedure()


customer_phone_list = [x[0] for x in getAllCustomerPhone()]

for i in range(8):
    print(f"----------------------  CUSTOMER {i} REVISIT -----------------------")
    existingCustomerComeback()
"""
customOrder()
