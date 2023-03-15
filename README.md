# Authentication-Backend-System

This is a simple authentication system for web application, implemented using FastAPI and SQLite. 

**Steps**

1. Clone the respository
2. Ensure that you have Python3 on Windows device before running  `.venv/Scripts/Activate` to activate the Virtual Environment 
3. Once in the Virtual Environement run `uvicorn src.main:app --reload` to start the program
4. Go to the port that this is running on and append `/docs#/` to it. For example `http://127.0.0.1:8000/docs#/`

<br>

**Below are the end points**

**For ADMIN/ TECHNICIAN/ MEMBER users**

* `POST /register` : Register Users into DB

* `POST /login`    : Login User

* `GET /users/me`  : Read User Information

* `PUT /users/me`  : Update User's Information

<br>

**Only for ADMIN users**

* `GET /users/admin/view`      : Admin view other users' Email and Roles

* `PUT /users/admin/update`    : Admin updates other user's roles

* `DELETE /users/admin/delete` : Admin delete other users