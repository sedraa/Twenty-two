import threading
from datetime import datetime, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os


from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
import sqlite3
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas

weburl = "http://127.0.0.1:5000"
app = Flask(__name__, template_folder='templates')
app.secret_key = "supersecretkey"

conn = sqlite3.connect('hotel.db', check_same_thread=False)
c = conn.cursor()


# Define routes

# route to homepage
@app.route('/')
def home():
    return render_template("home.html")


# route to login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # user provided formdata
        username = request.form["username"]
        password = request.form["password"]
        # Find the row with matching userdata
        c.execute("SELECT * FROM Guest WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        # if found load dashboard
        if user:
            session["user_id"] = user[0]
            return render_template("dashboard.html")
        # if not then again go to login page
        else:
            return render_template("login.html", error="Invalid username or password")
    else:
        return render_template("login.html")

def sendmail(userid,body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'your email id'
    sender_password = 'give mail app pwd not your actual password'

    c.execute("SELECT email FROM Guest WHERE id=?", (userid,))
    recipient_email = c.fetchall()[0][0]
    print(recipient_email)
    subject = 'Booking confirmation'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # log in to the SMTP server and send the message
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)


# route to register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # user provided formdata
        name = request.form["name"]
        username = request.form["username"]
        contact = request.form["contact"]
        email = request.form["email"]
        passport = request.form["passport"]
        dob = request.form["dob"]
        pincode = request.form["pincode"]
        password = request.form["password"]
        # store the data in table
        conn.execute(
            "INSERT INTO Guest (name, username, contact, email, passport, dob, pincode, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, username, contact, email, passport, dob, pincode, password))
        conn.commit()
        # redirect to login page
        return redirect(url_for("login"))
    else:
        return render_template("register.html")


# route to dashboard page
@app.route("/dashboard")
def dashboard():
    # check if user has loggedin or not
    user_id = session.get("user_id")
    if user_id:
        # if yes show dashboard page
        return render_template("dashboard.html")
    else:
        # else redirect user to login page
        return redirect(url_for("login"))


# route to get roomlist
@app.route("/room-list", methods=["GET", "POST"])
def roomdetails():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    else:
        # fetch roomlist from table
        c.execute('SELECT * FROM Rooms')
        rows = c.fetchall()
        roomlist = []
        for row in rows:
            roomlist.append({
                'id': row[0],
                'name': row[1],
                'price': row[2],
                'availability': row[3],
                'image_url': row[4]
            })
        return render_template('room_list.html', roomlist=roomlist)


# route to the new room booking form
@app.route("/new-booking", methods=["GET", "POST"])
def booking():
    # check user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        from_date = request.form["from-date"]
        to_date = request.form["to-date"]
        num_guest = request.form["num-guests"]
        room_type = request.form["room-type"]
        room_id = request.form["room-id"]
        print(room_id)
        # store the booking detail in table
        conn.execute(
            "INSERT INTO Booking (userid,room_id,from_date, to_date, num_guest, room_type,checkedIn,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, room_id, from_date, to_date, num_guest, room_type, 0, 'active'))
        query = "UPDATE Rooms SET availability = availability - 1 where id = " + room_id + ";"
        conn.execute(query)
        conn.commit()
        msg = "You have booked the room successfully, You can also self check in and check out"
        #send notification
        sendmail(user_id,msg)
        # show all orders page
        return redirect(
            "/all-orders/" + msg)
    else:
        return render_template("room_list.html")

# route to new form for booking taxi
@app.route("/taxi-booking", methods=["GET", "POST"])
def taxi_booking():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        time_g = request.form['time']
        # store taxi booking detail in table
        conn.execute("INSERT INTO TaxiBooking (userid,source, destination, DATE, TIME) VALUES (?, ?, ?, ?, ?)",
                     (user_id, source, destination, date, time_g))
        conn.commit()
        msg = "You taxi booking request is noted. Our representative will contact you once the booking get confirmed after checking available cab options."
        # send notification
        sendmail(user_id, msg)
        # send confirmation msg to user
        return jsonify({'redirect_url': "/all-orders/" + msg})
    else:
        return render_template("taxi_booking.html")


# route to page showing all oreders of user
@app.route("/all-orders/<string:msg>")
def all_orders(msg):
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    else:
        # Show all orders of user
        c.execute("SELECT * FROM Booking WHERE userid=?", (user_id,))
        roombookings = c.fetchall()
        c.execute("SELECT * FROM TaxiBooking WHERE userid=?", (user_id,))
        taxibookings = c.fetchall()
        c.execute("SELECT * FROM OrderedFood WHERE userid=?", (user_id,))
        foodbookings = c.fetchall()
        return render_template('all_orders.html', booking={'msg':msg,'room': roombookings, 'taxi': taxibookings,'food':foodbookings})


# route to form page taking new food order
@app.route("/order-food", methods=["GET", "POST"])
def order_food():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    if request.method == "POST":
        # user provided formdata
        order_data = request.get_json()
        delivery_date = order_data['delivery_date']
        delivery_time = order_data['delivery_time']
        food_items = []
        for item in order_data['food_order']:
            if item['count'] > 0:
                food_item = {
                    'food_id': item['id'],
                    'food_count': item['count'],
                    'food_name' : item['name'],
                    'food_price': item['price']
                }
                food_items.append(food_item)
        order = {
            'delivery_date': delivery_date,
            'delivery_time': delivery_time,
            'food_items': food_items
        }
        print(order['food_items'])
        for item in order['food_items']:
             conn.execute("INSERT INTO OrderedFood (food_id,userid,food_name,food_count,delivery_date, delivery_time,cost) VALUES (?, ?, ?, ?, ?, ?, ?)",(item['food_id'], user_id, item['food_name'], item['food_count'], order['delivery_date'], order['delivery_time'], item['food_price']))

        msg = "You food booking request is noted. Our representative will contact you once food will be ready to be delivered"
        # send notification
        sendmail(user_id, msg)
        conn.commit()
        return jsonify({'redirect_url': "/all-orders/"+msg})
    else:
        # fetch fooditems from table
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


# route to new page which will ask for user confirmation to set alarm
@app.route("/alarm/<string:alarm_datetime>")
def alarm(alarm_datetime):
    print(alarm_datetime)
    return render_template("alarm_page_keep_open.html", alarm_datetime=alarm_datetime)


# route to get alarm page
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
        # mpage mentioning alarm instruction
        return render_template("alarm_page.html", alarm_datetime=alarm_datetime)
    else:
        return render_template("wakeup_alarm.html")


# route to get self checkin and check out page
@app.route("/self-ci-co", methods=["GET", "POST"])
def selfcico():
    # check if user is logged in or not
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))
    else:
        c.execute("SELECT room_id,checkedIn,status FROM Booking WHERE userid=?", (user_id,))
        room_id, checkedIn, status= c.fetchall()[0]
        print(room_id,checkedIn,status)
        if room_id:
            if checkedIn == 0 and status=='active':
                finalurl = weburl + "/checkIn/" + str(room_id) + "/" + str(user_id)
            elif checkedIn == 1 and status=='active':
                finalurl = weburl + "/checkOut/" + str(room_id) + "/" + str(user_id)
            else:
                return "No booking available to check in"
            # create QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(finalurl)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # convert image to bytes
            buf = BytesIO()
            img.save(buf)

            # create response with QR code image
            response = make_response(buf.getvalue())
            response.headers['Content-Type'] = 'image/png'

            return response


@app.route("/checkIn/<int:room_id>/<int:user_id>", methods=["GET", "POST"])
def checkedIn(room_id,user_id):
    print(room_id,user_id)
    c.execute("SELECT checkedIn FROM Booking WHERE userid=? and room_id=? and status=?", (user_id,room_id,'active'))
    checkedIn= c.fetchall()[0][0]
    print(checkedIn)
    if checkedIn==0:
        c.execute("UPDATE Booking SET checkedIn = 1 where userid=? and room_id=? and status=?", (user_id,room_id,'active'))
        conn.commit()
        return "You have checked In successfully"
    return "No bookings found"

@app.route("/checkOut/<int:room_id>/<int:user_id>", methods=["GET", "POST"])
def checkedout(room_id,user_id):
    c.execute("SELECT checkedIn FROM Booking WHERE userid=? and room_id=? and status=?", (user_id,room_id,'active'))
    checkedIn= c.fetchall()[0][0]
    if checkedIn==1:
        c.execute("UPDATE Booking SET status = 'expired' where userid=? and room_id=? and status=?", (user_id,room_id,'active'))
        conn.commit()
        return "You have checked Out successfully"

@app.route("/vat-invoice", methods=["GET", "POST"])
def get_vat_invoice():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for("login"))
    food_cost = 0
    room_cost = 0

    # Fetch guest details
    cursor = conn.execute('SELECT name, username, contact, passport, dob, pincode FROM Guest WHERE id=?', (user_id,))
    guest_details = cursor.fetchone()

    # Fetch food items ordered by the user
    cursor = conn.execute('SELECT cost FROM OrderedFood WHERE userid=?', (user_id,))
    food_items = cursor.fetchall()
    if food_items:
        food_cost = sum(item[0] for item in food_items)

    # Fetch room booking cost (if any)
    cursor = conn.execute('SELECT room_id FROM Booking WHERE userid=?', (user_id,))
    room_booking = cursor.fetchone()
    if room_booking:
        room_id = room_booking[0]
        cursor = conn.execute('SELECT price FROM Rooms WHERE id=?', (room_id,))
        room_price = cursor.fetchone()[0]
        room_cost = room_price  # Assuming 1-night booking, adjust as needed

    # Calculate total cost
    total_cost = food_cost + room_cost

    # Create PDF invoice
    buffer = BytesIO()
    invoice = canvas.Canvas(buffer)
    # Add invoice details
    invoice.setTitle('VAT Invoice')
    invoice.drawString(80, 750, '**********Hotel Twenty Two********')
    invoice.drawString(150, 735, 'Invoice')
    invoice.drawString(80, 720, '-----------------------------------------------')
    invoice.drawString(50, 705, 'Customer Name: {}'.format(guest_details[0]))
    invoice.drawString(50, 680, 'Customer Username: {}'.format(guest_details[1]))
    invoice.drawString(50, 665, 'Date: {}'.format(datetime.now().strftime('%Y-%m-%d')))
    invoice.drawString(50, 650, 'Booking Charges:')
    if food_items:
        invoice.drawString(75, 635, 'Food Orders: ${}'.format(food_cost))
    if room_booking:
        invoice.drawString(75, 620, 'Room Booking: ${}'.format(room_cost))
    invoice.drawString(75, 605, 'Taxi Booking: $0.0 (Will be added once ride is completed)')
    invoice.drawString(50, 580, 'Total Amount Due: ${}'.format(total_cost))

    # Get PDF as bytes object
    invoice.save()
    pdf = buffer.getvalue()

    # Return PDF as response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=vat_invoice.pdf'
    return response


if __name__ == "__main__":
    app.run(debug=True)
