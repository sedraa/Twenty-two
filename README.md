# Twenty-two
Hotel Management System


# Used technologies:

HTML, CSS, Javascript, Bootstrap
Flask
sqlite3

# Introduction

Hospitability industry is growing with a very rapid pace. Every business owner wants to improve on
the services provided to the customer directly impacting the overall business growth. In this project
a Hotel Management System is designed to improve upon the overall customer experience. There
are many hotels running in the market providing best of the services, but most of them are focusing
mainly on customer acquisition rather than customer experience. For example, a customer books a
ticket online and checks in to the hotel. From here most of the problems starts showing up for the
customer and one of them are waiting in a queue for check in and check out. In this project similar
kind of different problems coming to the customer while staying in the hotel are identified. Those
problems which can be dealt with the help of hotel management system is implemented and the
resulting web app appears in minimizing the customer pain significantly.

Research Question or Problem that will be Addressed
The research question for this project is “What are the different kinds of problems a customer
staying in a hotel faces and how we can reduce or remove those problems with the help of web
application”

# Aim

The aim of this project is to implement different problem specific web components and integrate
them in hotel management system which will reduce some of the problems of user and increase
efficiency of the user.
Objectives
1. Develop a web app for hotel management system which will be desktop and mobile
compatible.
2. User can register and login into the system. All the benefits of the platform can only be
availed if user has successfully logged in into the system.
3. User will be shown with list of rooms which can be booked if available.
4. User would be able to self check in and check out.
5. While staying in the hotel user can order food from the given list of available options at
desired date and time.
6. While in stay if user wants to travel to some different location, then taxi can be booked from
the system. User would be free to choose source and destination location.
7. While in stay user can set and alarm which would wake up the user at desired date and time.
8. User can get the VAT invoice for different orders booked on the system while stay.

# Issues and Challenges faced
## 1. Taxi Booking functionality. 
Initially, for enabling user to give details of source, destination, date and time I implementated a simple form page with input text fields for source and destination.
The major issue is that the user need to type the source and destination addresses manually. This is alright, but the inputs will be error prone with typo issues and have inconsistency with the kind of address we want, for enhancing the app functionality by finding fare price between source and destination.
I search for different APIs and code snippet which will help me in populating the address automatically, according to the inputs user is providing. I got some of the APIs provided by google maps, bing map and other platforms but those were paid version. Since, I was looking for a free version, so I opted for Leaflet and OpenStreetMap API in my implementation. I have added the credit to those platform in the input field. However the API is free but it takes much time to make those work as there were some version issues which I got to deal with. I also faced lot of initial problem fetching the address values passed by user in the input fields using javascript, which could be send to backend to be stored.

## 2. Alarm setup:
I working with a webapp and only have the access to user's browser. So, it was quite challenging to set up an alarm in browser.
After searching for multiple solution in web, none of them was giving desired implementation. Most of them were either prompting a alert message or playing a sound from backend.
Then I tried to work along with my own implementation and successfully got the result. I tried below options in my implementation.
* Gave the user a form to enter the date and time for the alarm.
* Sent the provided data to flask backend.
* The API fetches the user provided data and open a new web page giving the instruction to user that "A new page has been open where you need to confirm that you need alarm, else you can close that tab." The purpose of this new tab is that the user can continue going through different webpages of the dashboard uniterrupting the alarm page.
* A new tab will be opened from the instruction page which will have a button asking user to confirm setting up the alarm. The main purpose of the button is to make user interact with the page so that the alarm mp3 file can be played. Without this I was getting an error mentioning "play() failed because the user didn't interact with the document first."

## 3. Room Booking page and Food order page
The basic functionalities for this page is implemented but need to be improved further. Currently I am looking for copyright free images for rooms and food items. I also have to write down some description of the hotel to attract the user.

## 4. Self check in and check out.
The main issue with this functionality is that how a user will have the access to the room as there is no room service and way to collect the key. The approach which can be used here is to design a QR code based on the room avalability and its unique identifier. There would be a qr code scanner in the room gate which will scan the qr code and allow user the access the room. Once the qr code is scanned the room will become unavailable for other users. Similarly there would be a qr code to check out, once scanned make the room available for other users.
