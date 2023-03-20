# Twenty-two
Hotel Management System


# Used technologies:

HTML, CSS, Javascript, Bootstrap
Flask
sqlite3

# Issues and Challenges faced
## 1. Taxi Booking functionality. 
Initially, for enabling user to give details of source, destination, date and time I implementated a simple form page with input text fields for source and destination.
The major issue is that the user need to type the source and destination addresses manually. This is alright, but the inputs will be error prone with typo issues and have inconsistency with the kind of address we want, for enhancing the app functionality by finding fare price between source and destination.
I search for different APIs and code snippet which will help me in populating the address automatically, according to the inputs user is providing. I got some of the APIs provided by google maps, bing map and other platforms but those were paid version. Since, I was looking for a free version, so I opted for Leaflet and OpenStreetMap API in my implementation. I have added the credit to those platform in the input field. However the API is free but it takes much time to make those work as there were some version issues which I got to deal with. I also faced lot of initial problem fetching the address values passed by user in the input fields using javascript, which could be send to backend to be stored.

## 2. Alarm setup:
We are working with a webapp and only have the access to user's browser. So, it was quite challenging to set up an alarm in browser.
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
