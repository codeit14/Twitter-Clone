# Twitter Clone
# Project Setup
The project backend has been implmented using Django-Rest-Framework and database used is RDBMS (MySQL). The code has been properly tested, and written in a generic manner. All the unit tests have been written in tests.py for each app[rest_auth and tweets].
Steps to setup the project on your machine- 
1) Create a virtual environment using command 
>         virtualenv venv -p python3
2) Activate virtual environment using command 
>         source venv/bin/activate
3) Install requirements using command
>         pip install -r requirements.txt
4) Create database in MySQL and save your database settings in local_settings.py(database, username and password)
5) Now make migrations of project using command 
>         python manage.py makemigrations && python manage.py migrate
6) Run Django server using command
>         python manage.py runserver
All ready to go !

# List of APIs and their functionalities (Note-  Except login and signup, each request requires an authentication token[TWEET {token_value}])
API | Request Body | Method | Description | Response
|---|---|---|---|---|
| [/rest_auth/signup/] | (first_name, last_name, username, password, email, contact_number(in +91 format), country_code) | POST | User Sign up  | Authentication Token
| [/rest_auth/login/] | (username, password) | POST | User Login | Authentication Token
| [/rest_auth/logout/] | No | GET | Logout User | No
| [/tweets/tweet/] | (attachments[Multiple], description) | POST | Post tweet with attachments | Tweet
| [/tweets/tweet/[Tweet_id]/] | No | GET | Retrieve Tweet Info | Tweet
| [/tweets/tweet/[Tweet_id]/] | No | DELETE | Delete Tweet | No
| [/tweets/tweet/user/[User_id]/] | No | GET | Get list of user's tweets | [Tweets]
| [/tweets/attachment/[Attachment_id]/] | No | GET | Get attachment details | Attachment
| [/tweets/follow/[User_id]/] | (is_follow) | PUT | Follow/Unfollow a User | No
| [/tweets/tweet/like/[Tweet_id]/] | (is_like) | PUT | Like/Unlike a Tweet | No
| [/rest_auth/user/[User_id]/] | No | GET | Get user's details | User
| [/tweets/tweet/retweet/post/[Tweet_id]/] | (comment) | POST | Retweet a tweet | No
| [/tweets/tweet/retweet/user/[User_id]/] | No | GET | Get user's retweets | [Retweets]
| [/tweets/tweet/retweet/read/[Retweet_id]/] | No | GET | Read a retweet | Retweet
| [/tweets/tweet/retweet/delete/[Retweet_id]/] | No | DELETE | Delete a retweet | No

# Postman Collection Link :)
https://www.getpostman.com/collections/0a1ef153f91b8b9663e3
