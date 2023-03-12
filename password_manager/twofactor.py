from twilio.rest import Client
import random
import sqlite3 as sql
import random
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(os.getenv('account_sid'), os.getenv('auth_token'))


def return_phone_number(id):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT phone_number FROM users WHERE user_id = ?", (id,))
        data = cur.fetchall()
        return data[0][0]


def send_otp(phone_number,otp):
    text = "Your verification code is: " + str(otp)
    message = client.messages.create(
    body = text, 
    from_ = os.getenv('twilio_number'), 
    to = phone_number
    )

def send_update(phone_number):
    text = "You have just made edits to your saved passwords."

    

    client.messages.create(
        body = text,
        from_ = os.getenv('twilio_number'),
        to = phone_number
    ) 

def send_update_personal(phone_number):
    text = "You have just made edits to your PMS account"

    

    client.messages.create(
        body = text,
        from_ = os.getenv('twilio_number'),
        to = phone_number
    ) 