# Flask Store Restful API

## Installation
```
pip install -r requirements.txt
python3 app.py
```
## Deployment

The following files are required for Heroku deployment
 
> - Profile
> - runtime.txt
> - uwsgi.ini

## Description
+ provide endpoints to list, retrieve, create, update and delete item and store

>	- GET `url/stores`
>	- GET `url/store/<string:name>`
>	- POST `url/store/<string:name>`
>	- DELETE `url/store/<string:name>`

>	- GET `url/items`
>	- GET `url/item/<string:name>`
>	- POST `url/item/<string:name>`
>	- DELETE `url/item/<string:name>`


+ Each store (id, name) contains list of item (id, name, price, store_id)

+ Also includes endpoints to register the user (id, username, password)

+ The caller of the endpoints is required to authenticate via /auth endpoint whereby a JWT token will be assigned for subsequent calls to the rest of endpoints

## Implementation
+ The endpoints are implemented using **Python Flask** micro framework and **SQLite**
