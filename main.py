from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = "supersecretkey"

# Create database connection
conn = sqlite3.connect('hotel.db', check_same_thread=False)
c = conn.cursor()

# Create table
#conn.execute("drop table Guest")
#conn.execute("drop table Booking")
conn.execute('''CREATE TABLE IF NOT EXISTS Guest
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL,
                contact TEXT NOT NULL,
                passport TEXT NOT NULL,
                dob TEXT NOT NULL,
                pincode TEXT NOT NULL,
                password TEXT NOT NULL);''')

conn.execute('''CREATE TABLE IF NOT EXISTS Booking
               (booking_id INTEGER PRIMARY KEY AUTOINCREMENT, id INTEGER, from_date TEXT, to_date TEXT, num_guest INTEGER, room_type TEXT);''')

conn.execute('''
           CREATE TABLE IF NOT EXISTS FoodItems (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               price REAL NOT NULL,
               availability BOOLEAN NOT NULL,
               image_url TEXT
           )
       ''')

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

conn.execute('''
           CREATE TABLE IF NOT EXISTS OrderedFood (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               food_id INTEGER NOT NULL,
               user_id INTEGER NOT NULL,
               FOREIGN KEY(food_id) REFERENCES FoodItems(id)
           )
       ''')
# Define routes

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        c.execute("SELECT * FROM Guest WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            session["user_id"] = user[0]
            return render_template("dashboard.html")
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        contact = request.form["contact"]
        passport = request.form["passport"]
        dob = request.form["dob"]
        pincode = request.form["pincode"]
        password = request.form["password"]
        conn.execute("INSERT INTO Guest (name, username, contact, passport, dob, pincode, password) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, username, contact, passport, dob, pincode, password))
        conn.commit()
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if user_id:
        return render_template("dashboard.html")
    else:
        return redirect(url_for("login"))

@app.route("/new-booking", methods=["GET", "POST"])
def booking():
    user_id = session.get("user_id")
    print(user_id)
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        from_date = request.form["from-date"]
        to_date = request.form["to-date"]
        num_guest = request.form["num-guest"]
        room_type = request.form["room-type"]
        conn.execute("INSERT INTO Booking (id, from_date, to_date, num_guest, room_type) VALUES (?, ?, ?, ?, ?)", (user_id, from_date, to_date, num_guest, room_type))
        conn.commit()
        return render_template("dashboard.html")
    else:
        return render_template("new_booking.html")

@app.route("/taxi-booking", methods=["GET", "POST"])
def taxi_booking():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        destination = request.form['destination']
        date = request.form['date']
        time = request.form['time']
        fare = request.form['fare']
    else:
        return render_template("taxi_booking.html")

@app.route("/all-orders")
def all_orders():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    else:
        c.execute("SELECT * FROM Booking WHERE id=?", (user_id,))
        bookings = c.fetchall()
        print(bookings)
        return render_template('all_orders.html', rows=bookings)


@app.route("/order-food", methods=["GET", "POST"])
def order_food():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        booking_id = request.form["booking_id"]
        c.execute("SELECT * FROM Bookings WHERE id=? AND user_id=?", (booking_id, user_id))
        booking = c.fetchone()
        if booking:
            return render_template("food_order.html")
        else:
            return render_template("food_order.html", error="Invalid booking ID")
    else:
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

if __name__ == "__main__":
    app.run(debug=True)
