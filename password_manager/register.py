import sqlite3 as sql
from tkinter import *
from phone_codes import *




def return_user_id(username):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        data = cur.fetchall()
        return data[0][0]

def concatenate_number(country, phone_number):
    code = country_codes[country]
    return code + phone_number[1:]
    
def check_username(username):
    #check if username is already taken
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        data = cur.fetchall()
        if len(data) > 0:
            return False
        else:
            return True
    
def check_password(password):
    #check if password is strong enough
    if len(password) < 12:
        return False
    capital_count = 0
    number_count = 0
    for i in password:
        if i.isalpha() and i.isupper():
            capital_count += 1
        if i.isdigit():
            number_count += 1
    if capital_count < 1 or number_count < 1:
        return False
    else:
        return True

def check_phone_number(phone_number):
    if len(phone_number) < 10:
        return False
    
    return True


    

def register(username, password, phone_number):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO users (username, pw, phone_number) VALUES (?, ?, ?)", (username, password, phone_number))
        con.commit()
    con.close()
    return True

