# A Stock exchange simulator
#### a stock exchange simulator which allows you to Quote, Buy, Sell, checking your payment History & Gain some fake revenue


##Main Functions:-
__________________


### 1.Register
______________
-On Get request:
	-Rendring registeration page ```register.html```.

-On Post request:
	-Create a Database query to Insert an new user with specific criteria.
	-Redirect user to login page



### 2.Login
___________
-On Get request:
	-Rendring login page ```login.html```.

-On Post request:
	-Create a Database query to Inquiry about user.
		-Rendring an error page if not exist.
	-Set user session.
	-Log user In ,Directing to Index page ```index.html```



### 3.Logout
____________
***@Login_Required***
>Supports Get request only.

-Clear user session.
-Log's user out.



### 5.Quote
___________
***@Login_Required***
-On Get request:
	-Rendring Quote page ```quote.html```.

-On Post request:
	-Search Stock price of inpputed symbol.
	-Render qutation about Stock price page ```quoted.html```.



### 5.Buy
_________
***@Login_Required***
-On Get request:
	-Rendring Buying page ```buy.html```.

-On Post request:
	-Calculate the amount of Cash for Stock's *Real time amount*.
	-Query Database to Subtract the amount of holding Cash.
	-Adding Stock's.
	-Redirect user to Index ```index.html```.



### 6.Sell
__________
***@Login_Required***
-On Get request:
	-Rendring Selling page ```sell.html```.

-On Post request:
	-Calculate the amount of Cash for Stock's *Real time amount*.
	-Query Database to adding the amount of holding Cash.
	-Removing Stock's.
	-Redirect user to Index ```index.html```.


### 7.History
_____________
***@Login_Required***
>Supports Get request only.

-Render ```history.html``` ,which display table of historical payments.



### 8.Index
___________
***@Login_Required***
>Supports Get request only.

-Render ```index.html``` ,which display table of holding Stock's, Cash flow, Currunt amount of holdings. 



### 9.Errorhandler
__________________
>API Error Handler.




##Helper Functions:-
____________________


### 1.Apology
_____________

-Rendring an apology Page with specific error message.


### 2.Login_required
____________________

-Login function dicoration.


### 3.Lookup
____________

-Query A real-time Database for Stock's.


### 4.USD
___________

-Format value as USD.


### 5.Validate
___________

-Validating *password* type only for requirments.
	-Must be more than 8 Digits.
	-Must be less than 12 Digits.
	-Must be Number's & Alphabetical's only



##Database Schema:
__________________

-CREATE TABLE users(id INTEGER,
username TEXT NOT NULL,
hash TEXT NOT NULL,
cash NUMERIC UNSIGNED NOT NULL DEFAULT 10000.00,
PRIMARY KEY(id));

-CREATE TABLE payments(transactionID INTEGER,
userID INTEGER NOT NULL,
symbol TEXT NOT NULL,
shares INTEGER NOT NULL,
date TEXT NOT NULL,
cost NUMERIC NOT NULL,
transaction_method TEXT NOT NULL,
balance_before NUMERIC NOT NULL,
balance_after NUMERIC NOT NULL,
PRIMARY KEY(transactionID),
FOREIGN KEY(userID) REFERENCES users(id));

-CREATE TABLE assets(userID INTEGER NOT NULL,
companyName TEXT NOT NULL,
symbol TEXT NOT NULL,
shares INTEGER NOT NULL,
holding_value NUMERIC NOT NULL,
FOREIGN KEY(userID) REFERENCES users(id));



##procedures:-
______________

-```Import``` Required libraris.
-configer Autoload.
-Ensure responses aren't cached.
-Configure session to use filesystem (instead of signed cookies).
-Connect BD.
-Run app. 