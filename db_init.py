import sqlite3

# Create database connection
conn = sqlite3.connect('hotel.db', check_same_thread=False)
c = conn.cursor()
conn.execute("Drop table TaxiBooking")
conn.execute("Drop table FoodItems")
conn.execute("Drop table Booking")
conn.execute("Drop table Rooms")
conn.execute("Drop table OrderedFood")

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
               (booking_id INTEGER PRIMARY KEY AUTOINCREMENT, userid INTEGER,room_id INTEGER, from_date TEXT, to_date TEXT, num_guest INTEGER, room_type TEXT,checkedIn INTEGER,status TEXT);''')

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


conn.execute('''
           CREATE TABLE IF NOT EXISTS Rooms (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               price REAL NOT NULL,
               availability BOOLEAN NOT NULL,
               image_url TEXT
           )
       ''')

rooms_data = [
    ('Standard Room', 100.0, 5, 'static/hotelrooms/standard.jpg'),
    ('Deluxe Suite', 250.0, 4, 'static/hotelrooms/deluxe.jpg'),
    ('Executive Room', 175.0, 2, 'static/hotelrooms/executive.jpg'),
    ('Twin Room', 90.0, 3, 'static/hotelrooms/twin.jpg'),
    ('Budget Room', 50.0, 10, 'static/hotelrooms/budget.jpg')
]

query = '''
    INSERT INTO Rooms (name, price, availability, image_url)
    VALUES (?, ?, ?, ?)
'''

conn.executemany(query, rooms_data)
conn.commit()

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
    ('Hamburger', 5.99, 10, 'static/fooditems/hamburger.jpg'),
    ('Cheese Pizza', 9.99, 7, 'static/fooditems/pizza.jpg'),
    ('Fried Chicken', 7.99, 12, 'static/fooditems/chicken.jpg'),
    ('Caesar Salad', 4.99, 8, 'static/fooditems/salad.jpg'),
    ('Spaghetti Bolognese', 12.99, 5, 'static/fooditems/spaghetti.jpg')
]
c.executemany(query, food_items)
conn.commit()

#OrderedFood table with fields like id,food_id,user_id,food_name,food_count,delivery_date, delivery_time,cost
conn.execute('''
           CREATE TABLE IF NOT EXISTS OrderedFood (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               food_id INTEGER NOT NULL,
               userid INTEGER NOT NULL,
               food_name TEXT,
               food_count INTEGER,
               delivery_date TEXT,
               delivery_time TEXT,
               cost INTEGER,
               FOREIGN KEY(food_id) REFERENCES FoodItems(id)
           )
       ''')
