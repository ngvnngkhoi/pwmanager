from tkinter import *
from register import *
from hashlib import *
import sqlite3 as sql
from qrcode import QRCode
from PIL import ImageTk   
from twofactor import *
import random
from phone_codes import country_list

class login_page:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        header = Label(text="Password Management System", font=("Arial", 20))

        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users")
            data = cur.fetchall()
            usernames = [data[i][0] for i in range(len(data))]
            if len(usernames) == 0:
                usernames.append("Please register a profile.")
        
        self.clicked = StringVar()
        self.clicked.set("Select a Profile")
        self.profile = OptionMenu(self.root, self.clicked, *usernames)


        password_label = Label(text="Password")
        self.username_input = Entry()
        self.password_input = Entry(show = '*')
        login_btn = Button(text="Login", command=self.login)
        register_btn = Button(text="Register", command=self.register)

        self.remember_me = BooleanVar()
        self.remember_me.set(1)
        self.remember_me = Checkbutton(text = "Remember me", variable = self.remember_me, onvalue = 1, offvalue = 0, height=5, width = 20)

        self.remember_me.place(x=100, y=350)
        self.profile.place(x=100, y=150)
        header.place(x=60, y=100)
        password_label.place(x=100, y=250)
        self.password_input.place(x=200, y=250)
        login_btn.place(x=100, y=300)
        register_btn.place(x=200, y=300)

        if self.remember_me == 1:
            with sql.connect("database.db") as con:
                #check if there are other users with remember me checked
                cur = con.cursor()
                cur.execute("SELECT * FROM user_setting WHERE remember_me = TRUE")
                data = cur.fetchall()

                if len(data) == 1 and self.username_input.get() == data[0][0]:
                    self.login()
                elif len(data) == 1 and self.username_input.get() != data[0][0]:
                    cur.execute("UPDATE user_setting SET remember_me = FALSE WHERE user_id = ?", (data[0][1],))
                    cur.execute("UPDATE user_setting SET remember_me = TRUE WHERE user_id = ?", (return_user_id(self.username_input.get()),))
                
                elif len(data) > 1:
                    for i in range(len(data)):
                        cur.execute("UPDATE user_setting SET remember_me = FALSE WHERE user_id = ?", (data[i][1],))
                    
                    cur.execute("UPDATE user_setting SET remember_me = TRUE WHERE user_id = ?", (return_user_id(self.username_input.get()),))
                
                elif len(data) == 0:
                    cur.execute("UPDATE user_setting SET remember_me = TRUE WHERE user_id = ?", (return_user_id(self.username_input.get()),))
                    
    def login(self):
        if self.clicked.get() == "Select a Profile":
            error_label = Label(text="Please select a profile.")
            error_label.place(x=250, y=400)

        if self.clicked.get() != "Select a Profile":
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (self.clicked.get(),))
                data = cur.fetchall()
            with sql.connect("database.db") as conn:
                cur = conn.cursor()
                cur.execute("Select * FROM user_setting where user_id = ?", (return_user_id(self.clicked.get()),))
                data2 = cur.fetchall()
            
                if len(data) == 0:
                    error_label = Label(text="Username does not exist.")
                    error_label.place(x=250, y=400)
                elif data[0][1] != sha256(self.password_input.get().encode()).hexdigest():
                    error_label = Label(text="Incorrect password.")
                    error_label.place(x=250, y=400)
                if data2[0][1] == 1 and data[0][1] == sha256(self.password_input.get().encode()).hexdigest():
                    generate_otp = random.randint(10000, 99999)
                    send_otp(return_phone_number(return_user_id(self.clicked.get())), generate_otp)
                    otp_input = Entry()
                    otp_input.place(x=200, y=350)
                    confirm_btn = Button(text="Confirm", command=lambda: self.confirm(otp_input.get(),generate_otp))
                    confirm_btn.place(x=100, y=350)
                else:
                    self.root.destroy()
                    username = self.clicked.get()
                    main_page(username, return_user_id(username))

    def confirm(self, otp_input , generate_otp):
        if int(otp_input) == generate_otp:
            self.root.destroy()
            username = self.clicked.get()
            main_page(username, return_user_id(username))
        if int(otp_input) != generate_otp:
            error_label = Label(text="Incorrect OTP.")
            error_label.place(x=250, y=400)


    def register(self):
        #switch to register page
        self.root.destroy()
        register_page()


class register_page:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        header = Label(text="Create an account", font=("Arial", 20))

        username_label = Label(text="Username")
        password_label = Label(text="Password")
        reenter_password_label = Label(text="Confirm Password")
        phone_number_label = Label(text="Phone Number")
        self.clicked = StringVar()
        self.clicked.set("Country Code")
        self.country_code = OptionMenu(self.root, self.clicked, *country_list)
        self.country_code.place(x=250, y=270)


        self.username_input = Entry()
        self.password_input = Entry(show = '*')
        self.reenter_password_input = Entry(show = '*')
        self.phone_number_input = Entry()

        register_btn = Button(text="Register", command=self.register)
        return_btn = Button(text="Return", command=self.back)

        username_label.place(x=100, y=100)
        password_label.place(x=100, y=150)
        reenter_password_label.place(x=100, y=200)
        phone_number_label.place(x=100, y=250)

        self.username_input.place(x=250, y=100)
        self.password_input.place(x=250, y=150)
        self.reenter_password_input.place(x=250, y=200)
        self.phone_number_input.place(x=250, y=250)
        #place top right corner of window at 
        register_btn.place(x = 300, y = 35 )
        return_btn.place(x=400, y= 35)


        header.place(x=35, y=25)

    def register(self):
        errors = []
        if check_username(self.username_input.get()) == False:
            errors.append("Username already exists.")

        if check_password(self.password_input.get()) == False:
            errors.append("Password must be at least 12 characters long and contain at least one letter and one number.")

        if self.password_input.get() != self.reenter_password_input.get():
            errors.append("Passwords do not match.")

        if check_phone_number(self.phone_number_input.get()) == False:
            errors.append("Phone number must be 10 digits long.")
        
        if len(errors) > 0:
            error_label = Label(text=errors[0])
            if errors[0] == "Password must be at least 12 characters long and contain at least one letter and one number.":
                error_label.place(x=5   , y=400)
            else:
                error_label.place(x=250, y=400)

        if check_password(self.password_input.get()) and check_username(self.username_input.get()) and check_phone_number(self.phone_number_input.get()) and self.password_input.get() == self.reenter_password_input.get():
            otp = random.randint(1000000,9999999)
             #get dropdown value here and concatenate it with the phone number
            if self.clicked.get() == "Country Code":
                error = Label(text="Please select a country code.")
                error.place(x=250, y=400)
            else:
                number = concatenate_number(self.clicked.get(), self.phone_number_input.get())
                send_otp(number, otp)
                self.otp_input = Entry()
                self.otp_input.place(x=250, y=300)
                otp_label = Label(text="Enter OTP")
                otp_label.place(x=100, y=300)
                confirm_btn = Button(text="Confirm", command=lambda: self.confirm(self.otp_input.get(), otp))
                #place next to otp input
                confirm_btn.place(x=300, y=350)

    def confirm(self, otp_input, otp):
        if otp_input == str(otp):
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, pw, phone_number) VALUES (?,?,?)", (self.username_input.get(), sha256(self.password_input.get().encode()).hexdigest(), concatenate_number(self.clicked.get(), self.phone_number_input.get())))
                con.commit()
                cur.execute("INSERT INTO user_setting(user_id, two_factor_login, auto_launch_websites) VALUES (?,?,?)", (return_user_id(self.username_input.get()), 1, 1))
                con.commit() 
            self.root.destroy()
            username = self.username_input.get()
            main_page(username, return_user_id(username))
        else:
            error = Label(text="Incorrect OTP.")
            error.place(x = 100, y = 450)

    def back(self):
        self.root.destroy()
        login_page()

class main_page:
    def __init__(self,username,user_id):
        self.user_id = user_id
        self.username = username
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        #print current username_input
        current_session = 'Current session user: ' + username
        header = Label(text=current_session, font=("Arial", 10))
        header.place(x=10, y=15)
        logout_btn = Button(text="Logout", command=self.logout)
        new_password_button = Button(text = "New Password", command = self.create_new_password)
        change_information_btn = Button(text="Change Information", command=self.change_information)
        settings_btn = Button(text = "Settings", command = self.settings)

        change_information_btn.place(x=10, y=65)
        logout_btn.place(x=240, y=65)
        new_password_button.place(x=140, y=65)
        settings_btn.place(x=400, y=65)
    

        #display all name columns for user id
        my_pass_label = Label(text="My Passwords: ", font=("Arial", 20))
        my_pass_label.place(x=100, y=150)
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT name FROM passwords WHERE user_id = ?", (user_id,))
            data = cur.fetchall()
        b,i,j,count = 0,0,0,0
        while True:
            name = data[i][0]
            name_btn = Button(text=name, command=lambda name=name: self.open_password(name))
            name_btn.place(x=100+ (100*b), y= 200 + (j*50))
            count += 1
            j += 1
            i += 1
            if count == 5:
                b += 1
                j = 0
            
            if count == len(data):
                break
              
    def change_information(self):
        self.root.destroy()
        change_information_page(self.username,self.user_id)
            
    def create_new_password(self):
        self.root.destroy()
        new_password_page(self.username,self.user_id)
    
    def open_password(self,name):
        self.root.destroy()
        password_page(self.username,self.user_id,name)

    def settings(self):
        self.root.destroy()
        settings_page(self.username,self.user_id)

    def logout(self):
        self.root.destroy()
        login_page()

class new_password_page():
    def __init__(self,username,id):
        self.username = username
        self.id = id
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        #print current username_input
        current_session = 'Current session user: ' + username
        header = Label(text=current_session, font=("Arial", 10))
        header.place(x=10, y=15)
        new_password_button = Button(text = "Generate new password", command = self.create_new_password)
        name_label = Label(text = "Name of account: ")
        username_label = Label(text = "Username: ")
        password_label = Label(text = "Password: ")
        link_label = Label(text = "Link: ")
        special_notes_label = Label(text = "Special Notes: ")
        go_back_btn = Button(text = "Go back", command = self.go_back)

        self.name_input = Entry()    
        self.username_input = Entry()
        self.password_input = Entry(show = '*')
        self.link_input = Entry()
        self.special_notes_input = Entry()
        
        name_label.place(x=100, y=200)
        username_label.place(x=100, y=250)
        password_label.place(x=100, y=300)
        link_label.place(x=100, y=350)
        special_notes_label.place(x=100, y=400)
        self.name_input.place(x=250, y=200)
        self.username_input.place(x=250, y=250)
        self.password_input.place(x=250, y=300)
        self.link_input.place(x=250, y=350)
        self.special_notes_input.place(x=250, y=400)
        new_password_button.place(x=100, y=100)
        go_back_btn.place(x=400, y=10)
    
    def create_new_password(self):
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("INSERT INTO passwords (name, username, pw, link, special_notes, user_id) VALUES (?,?,?,?,?,?)",(self.name_input.get(),self.username_input.get(),self.password_input.get(),self.link_input.get(),self.special_notes_input.get(),self.id))
            db.commit()
            success = Label(text="Password created successfully.")
            success.place(x = 100, y = 450)
            self.name_input.delete(0, END)
            self.username_input.delete(0, END)
            self.password_input.delete(0, END)
            self.link_input.delete(0, END)
            self.special_notes_input.delete(0, END)
        
    def go_back(self):
        self.root.destroy()
        main_page(self.username,self.id) 


class password_page():
    def __init__(self,username,id,name):
        self.username = username
        self.id = id
        self.name = name
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        #print current username_input
        current_account = 'Current account: ' + name
        header = Label(text=current_account, font=("Arial", 10))
        header.place(x=10, y=15)
        edit_btn = Button(text = "Edit", command = self.edit)
        edit_btn.place(x=400, y=30)
        delete_btn = Button(text = "Delete", command = self.delete)
        delete_btn.place(x=400, y=60)
        go_back_btn = Button(text = "Go back", command = self.go_back)
        go_back_btn.place(x=400, y=90)
        with sql.connect("database.db") as db:
            cur = db.cursor()
            #select link 
            cur.execute("SELECT link FROM passwords WHERE name = ? AND user_id = ?", (name,id))
            data = cur.fetchall()
            link = data[0][0]
            qr = QRCode(version=1, box_size=5, border=0)
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')
            qr_code = ImageTk.PhotoImage(img)
            qr_label = Label(image=qr_code, height = 170, width = 170)
            qr_label.image = qr_code
            qr_label.place(x=25, y=35)

        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM passwords WHERE name = ? AND user_id = ?", (name,id))
            data = cur.fetchall()
            name_label = Label(text = "Name of account: " + data[0][0])
            username_label = Label(text = "Username: " + data[0][1])
            password_label = Label(text = "Password: " + data[0][2])
            #create a link to the website
            link_label = Label(text = "Link: " + data[0][3])
            special_notes_label = Label(text = "Special Notes: " + data[0][4])
            name_label.place(x=100, y=200)
            username_label.place(x=100, y=250)
            password_label.place(x=100, y=300)
            link_label.place(x=100, y=350)
            special_notes_label.place(x=100, y=400)
    
    def go_back(self):
        self.root.destroy()
        main_page(self.username,self.id)
    
    def edit(self):
        self.root.destroy()
        edit_page(self.username,self.id,self.name)
    
    def delete(self):
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("DELETE FROM passwords WHERE name = ? AND user_id = ?", (self.name,self.id))
            db.commit()
            self.root.destroy()
            main_page(self.username,self.id)

class edit_page():
    def __init__(self,username,user_id,name):
        self.user_id = user_id
        self.name = name
        self.username = username
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        #print current username_input
        current_account = 'Current account: ' + name
        header = Label(text=current_account, font=("Arial", 10))
        header.place(x=10, y=15)
        save_btn = Button(text = "Save", command = self.save)
        save_btn.place(x=400, y=30)
        go_back_btn = Button(text = "Go back", command = self.go_back)
        go_back_btn.place(x=400, y=10)
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM passwords WHERE name = ? AND user_id = ?", (name,user_id))
            data = cur.fetchall()
            name_label = Label(text = "Name of account: ")
            username_label = Label(text = "Username: ")
            password_label = Label(text = "Password: ")
            link_label = Label(text = "Link: ")
            special_notes_label = Label(text = "Special Notes: ")
            name_label.place(x=100, y=200)
            username_label.place(x=100, y=250)
            password_label.place(x=100, y=300)
            link_label.place(x=100, y=350)
            special_notes_label.place(x=100, y=400)
            self.name_input = Entry()    
            self.username_input = Entry()
            self.password_input = Entry(show = '*')
            self.link_input = Entry()
            self.special_notes_input = Entry()
            self.name_input.insert(0,data[0][0])
            self.username_input.insert(0,data[0][1])
            self.password_input.insert(0,data[0][2])
            self.link_input.insert(0,data[0][3])
            self.special_notes_input.insert(0,data[0][4])
            self.name_input.place(x=250, y=200)
            self.username_input.place(x=250, y=250)
            self.password_input.place(x=250, y=300)
            self.link_input.place(x=250, y=350)
            self.special_notes_input.place(x=250, y=400)
    
    def save(self):
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("UPDATE passwords SET name = ?, username = ?, pw = ?, link = ?, special_notes = ? WHERE name = ? AND user_id = ?", (self.name_input.get(),self.username_input.get(),self.password_input.get(),self.link_input.get(),self.special_notes_input.get(),self.name,self.user_id))
            db.commit()
            self.root.destroy()
            send_update(return_phone_number(self.user_id))
            main_page(self.username,self.user_id)
    
    def go_back(self):
        self.root.destroy(return_phone_number(self.user_id))
        main_page(self.username,self.user_id)

class change_information_page():
    def __init__(self,username,user_id):
        self.user_id = user_id
        self.username = username
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.root.title("Password Management System")
        #print current username_input
        current_account = 'Current account: ' + username
        header = Label(text=current_account, font=("Arial", 10))
        header.place(x=10, y=15)
        save_btn = Button(text = "Save", command = self.save)
        save_btn.place(x=400, y=30)
        go_back_btn = Button(text = "Go back", command = self.go_back)
        go_back_btn.place(x=400, y=10)



        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            data = cur.fetchall()
            username_label = Label(text = "Username: ")
            password_label = Label(text = "Password: ")
            phone_number_label = Label(text = "Phone Number: ")
            username_label.place(x=100, y=200)
            password_label.place(x=100, y=250)
            phone_number_label.place(x=100, y=300)
            self.username_input = Entry()    
            self.password_input = Entry(show = '*')
            self.phone_number_input = Entry()
            

            self.username_input.insert(0,data[0][0])
            self.password_input.insert(0,data[0][1])
            self.phone_number_input.insert(0,data[0][2])
            self.username_input.place(x=250, y=200)
            self.password_input.place(x=250, y=250)
            self.phone_number_input.place(x=250, y=300)
    
    def save(self):
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("UPDATE users SET username = ?, pw = ?, phone_number = ?, sms = ?, 2FA = ? WHERE user_id = ?", (self.username_input.get(),self.password_input.get(),self.phone_number_input.get(),self.user_id, ))
            db.commit()
            self.root.destroy()
            send_update_personal(return_phone_number(self.user_id))
            main_page(self.username,self.user_id)

    
    def go_back(self):
        self.root.destroy()
        main_page(self.username,self.user_id)


class settings_page():
    def __init__(self, username, user_id) -> None:
        self.username = username
        self.user_id = user_id
        self.root = Tk()
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.root.title("Password Management System")
        #print current username_input

        current_account = 'Current account: ' + username
        header = Label(text=current_account, font=("Arial", 10))
        header.place(x=10, y=15)
        save_btn = Button(text = "Save", command = self.save)
        save_btn.place(x=400, y=30)
        go_back_btn = Button(text = "Go back", command = self.go_back)
        go_back_btn.place(x=400, y=10)

        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM user_setting WHERE user_id = ?", (user_id,))
            data = cur.fetchall()

        #create a checkbox, if checked, 2FA is true, if not, 2FA is false
        self.two_factor_input = BooleanVar()
        self.two_factor_input.set(data[0][1])
        self.two_factor_checkbox = Checkbutton(text = "2FA", variable = self.two_factor_input)

        self.two_factor_checkbox.place(x=100, y=200)

        self.auto_launch_input = BooleanVar()
        self.auto_launch_input.set(data[0][2])
        self.auto_launch_checkbox = Checkbutton(text = "Auto launch websites", variable = self.auto_launch_input)

        self.auto_launch_checkbox.place(x=100, y=250)

        
    def save(self):
        with sql.connect("database.db") as db:
            cur = db.cursor()
            cur.execute("UPDATE user_setting SET two_factor_login = ?, auto_launch_websites = ? WHERE user_id = ?", (self.two_factor_input.get(),self.auto_launch_input.get(),self.user_id))
            db.commit()
            self.root.destroy()
            send_update_personal(return_phone_number(self.user_id))
            main_page(self.username,self.user_id)
    
    def go_back(self):
        self.root.destroy()
        main_page(self.username,self.user_id)
    

        


    
if __name__ == "__main__":
    with sql.connect("database.db") as db:
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS user_setting (user_id INTEGER, two_factor_login BOOLEAN, auto_launch_websites BOOLEAN, remember_me BOOLEAN)")
        cur.execute("CREATE TABLE IF NOT EXISTS passwords (name TEXT, username TEXT, pw TEXT, link TEXT, special_notes TEXT ,user_id INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, pw TEXT, phone_number TEXT, user_id INTEGER PRIMARY KEY AUTOINCREMENT)")
        data = cur.fetchall()
        db.commit()
    with sql.connect("database.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM user_setting where remember_me = TRUE")
        data = cur.fetchall()
        db.commit()

    if len(data) == 0:
        login_page()
    else:
        main_page(data[0][0],data[0][1])
    mainloop()
