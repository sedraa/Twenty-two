import threading
from datetime import datetime, time

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = "supersecretkey"

# Create database connection
conn = sqlite3.connect('hotel.db', check_same_thread=False)
c = conn.cursor()
conn.execute("Drop table TaxiBooking")
conn.execute("Drop table Booking")
# Create required tables

#guest table which will have fields id,name,username,contact,passport,dob,pincode and password.
conn.execute('''CREATE TABLE IF NOT EXISTS Guest
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                contact TEXT NOT NULL,
                passport TEXT NOT NULL,
                dob TEXT NOT NULL,
                pincode TEXT NOT NULL,
                password TEXT NOT NULL);''')

#Booking table which has field like booking_id, id, from_date, to_date, num_guest,room_type
conn.execute('''CREATE TABLE IF NOT EXISTS Booking
               (booking_id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER, from_date TEXT, to_date TEXT, num_guest INTEGER, room_type TEXT);''')

#FoodItems with fields id, name, price, availability and image_url
conn.execute('''
           CREATE TABLE IF NOT EXISTS FoodItems (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               price REAL NOT NULL,
               availability BOOLEAN NOT NULL,
               image_url TEXT
           )
       ''')

#Taxibooking table with fields like tbookingid, id,source,destination,DATE and TIME
conn.execute('''
           CREATE TABLE IF NOT EXISTS TaxiBooking (
               tbookingid INTEGER PRIMARY KEY AUTOINCREMENT,
               userid Integer NOT NULL,
               source TEXT NOT NULL,
               destination TEXT NOT NULL,
               DATE TEXT NOT NULL,
               TIME TEXT NOT NULL
           )
       ''')

#insert fooditems in the table which will be shown to the user
query = """INSERT INTO FoodItems (name, price, availability, image_url)
         VALUES (?, ?, ?, ?)"""
food_items = [
    ('Hamburger', 5.99, 10, 'https://example.com/hamburger.jpg'),
    ('Cheese Pizza', 9.99, 7, 'https://example.com/pizza.jpg'),
    ('Fried Chicken', 7.99, 12, 'https://example.com/chicken.jpg'),
    ('Caesar Salad', 4.99, 8, 'https://example.com/salad.jpg'),
    ('Spaghetti Bolognese', 12.99, 5, 'https://example.com/spaghetti.jpg')
]
c.executemany(query, food_items)
conn.commit()

#OrderedFood table with fields like id,food_id,user_id
conn.execute('''
           CREATE TABLE IF NOT EXISTS OrderedFood (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               food_id INTEGER NOT NULL,
               user_id INTEGER NOT NULL,
               FOREIGN KEY(food_id) REFERENCES FoodItems(id)
           )
       ''')
# Define routes

#route to homepage
@app.route('/')
def home():
    return render_template("home.html")

#route to login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #user provided formdata
        username = request.form["username"]
        password = request.form["password"]
        #Find the row with matching userdata
        c.execute("SELECT * FROM Guest WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        #if found load dashboard
        if user:
            session["user_id"] = user[0]
            return render_template("dashboard.html")
        #if not then again go to login page
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

#route to register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #user provided formdata
        name = request.form["name"]
        username = request.form["username"]
        contact = request.form["contact"]
        passport = request.form["passport"]
        dob = request.form["dob"]
        pincode = request.form["pincode"]
        password = request.form["password"]
        #store the data in table
        conn.execute("INSERT INTO Guest (name, username, contact, passport, dob, pincode, password) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, username, contact, passport, dob, pincode, password))
        conn.commit()
        #redirect to login page
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

#route to dashboard page
@app.route("/dashboard")
def dashboard():
    #check if user has loggedin or not
    user_id = session.get("user_id")
    if user_id:
        #if yes show dashboard page
        return render_template("dashboard.html")
    else:
        #else redirect user to login page
        return redirect(url_for("login"))

#route to the new room booking form
@app.route("/new-booking", methods=["GET", "POST"])
def booking():
    #check user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        #user provided formdata
        from_date = request.form["from-date"]
        to_date = request.form["to-date"]
        num_guest = request.form["num-guest"]
        room_type = request.form["room-type"]
        #store the booking detail in table
        conn.execute("INSERT INTO Booking (userid, from_date, to_date, num_guest, room_type) VALUES (?, ?, ?, ?, ?)", (user_id, from_date, to_date, num_guest, room_type))
        conn.commit()
        #show all orders page
        return redirect("/all-orders")
    else:
        return render_template("new_booking.html")

#route to new form for booking taxi
@app.route("/taxi-booking", methods=["GET", "POST"])
def taxi_booking():
    #check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        time_g = request.form['time']
        #store taxi booking detail in table
        conn.execute("INSERT INTO TaxiBooking (userid,source, destination, DATE, TIME) VALUES (?, ?, ?, ?, ?)",(user_id, source, destination, date, time_g))
        #send confirmation msg to user
        return render_template("taxi_booking_conf.html")
    else:
        return render_template("taxi_booking.html")

#route to page showing all oreders of user
@app.route("/all-orders")
def all_orders():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    else:
        #Show all orders of user
        c.execute("SELECT * FROM Booking WHERE userid=?", (user_id,))
        roombookings = c.fetchall()
        c.execute("SELECT * FROM TaxiBooking WHERE userid=?", (user_id,))
        taxibookings = c.fetchall()
        return render_template('all_orders.html', booking={'room':roombookings,'taxi':taxibookings})

#route to form page taking new food order
@app.route("/order-food", methods=["GET", "POST"])
def order_food():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        booking_id = request.form["booking_id"]
        c.execute("SELECT * FROM Bookings WHERE id=? AND user_id=?", (booking_id, user_id))
        booking = c.fetchone()
        if booking:
            return render_template("food_order.html")
        else:
            return render_template("food_order.html", error="Invalid booking ID")
    else:
        #fetch fooditems from table
        c.execute('SELECT * FROM FoodItems')
        rows = c.fetchall()
        food_items = []
        for row in rows:
            food_items.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'availability': row[3],
                'image_url': row[4]
            })
        return render_template('order_food.html', food_items=food_items)

#route to new page which will ask for user confirmation to set alarm
@app.route("/alarm/<string:alarm_datetime>")
def alarm(alarm_datetime):
    print(alarm_datetime)
    return render_template("alarm_page_keep_open.html", alarm_datetime=alarm_datetime)

#route to get alarm page
@app.route("/wakeup-alarm", methods=["GET", "POST"])
def alarm_setup():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        alarm_date = request.form['date']
        alarm_time = request.form['time']
        alarm_datetime = alarm_date + " " + alarm_time
        #mpage mentioning alarm instruction
        return render_template("alarm_page.html", alarm_datetime=alarm_datetime)
    else:
        return render_template("wakeup_alarm.html")
if __name__ == "__main__":
    app.run(debug=True)
