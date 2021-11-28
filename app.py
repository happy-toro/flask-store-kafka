from os import environ
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from jwt_impl import (blocklist,
                      JWT_RSA_PRIVATE,
                      JWT_RSA_PUBLIC,
                      JWT_ACCESS_EXPIRES,
                      JWT_REFRESH_EXPIRES)
from resources.user import (UserRegister,
                            UserLogin,
                            UserLogout,
                            User,
                            UserTokenRefresh)
from resources.store import Store, StoreList
from resources.item import Item, ItemList


app = Flask(__name__)

# create database
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.before_first_request
def create_all_table():
    db.create_all()  # create all tables before first call


# set up JWT authentication
#   ONLY FOR SYMMETRY JWT
#   app.config['JWT_SECRET_KEY'] = 'happy-toro-secret-key'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_PRIVATE_KEY'] = JWT_RSA_PRIVATE
app.config['JWT_PUBLIC_KEY'] = JWT_RSA_PUBLIC
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_EXPIRES
app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    return {'is_admin': bool(identity == 1)}


@jwt.token_in_blocklist_loader
def is_in_blocklist(jwt_header, jwt_payload):
    token_jti = jwt_payload['jti']
    return bool(blocklist.exists(token_jti))


# set up restful endpoints
api = Api(app)
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/auth')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserTokenRefresh, '/non-fresh-token')
api.add_resource(User, '/user/<string:username>')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
