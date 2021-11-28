from time import time
from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                get_jwt,
                                get_jti,
                                get_jwt_identity)
from werkzeug.security import safe_str_cmp

from resources.http_code import (HTTP_OK,
                                 HTTP_CREATED,
                                 HTTP_BAD_REQUEST,
                                 HTTP_UNAUTHORIZED,
                                 HTTP_NOT_FOUND)
from models.user import UserModel
from jwt_impl import (blocklist,
                      JWT_ACCESS_EXPIRES,
                      JWT_REFRESH_EXPIRES)
from outbox import produce_event

_parser = reqparse.RequestParser()
_parser.add_argument('username',
                     type=str,
                     required=True,
                     help='Username is required')
_parser.add_argument('password',
                     type=str,
                     required=True,
                     help='Password is required')


class UserRegister(Resource):
    @staticmethod
    def post():
        data = _parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return ({'message':
                    f'Username {data["username"]!r} is used'},
                    HTTP_BAD_REQUEST)

        new_user = UserModel(**data)
        new_user.save_to_db()
        produce_event(new_user.id, 'create', 'user', new_user.json())
        return ({'message':
                f'User {data["username"]!r} is created'},
                HTTP_CREATED)


class User(Resource):
    @staticmethod
    @jwt_required(fresh=True)
    def get(username):
        claims = get_jwt()
        if not claims['is_admin']:
            return ({'message': 'Admin privilege is required to view user detail'},
                    HTTP_UNAUTHORIZED)

        target_user = UserModel.find_by_username(username)
        if target_user:
            return target_user.json(), HTTP_OK
        else:
            return ({'message': f'User {username!r} does not exist'},
                    HTTP_NOT_FOUND)

    @staticmethod
    @jwt_required(fresh=True)
    def delete(username):
        claims = get_jwt()
        if not claims['is_admin']:
            return ({'message': 'Admin privilege is required to delete user'},
                    HTTP_UNAUTHORIZED)

        target_user = UserModel.find_by_username(username)
        if target_user:
            event_detail = target_user.json()
            target_user.delete_from_db()
            produce_event(get_jwt_identity(), 'delete', 'user', event_detail)
            return ({'message': f'User {username!r} is deleted'},
                    HTTP_OK)
        else:
            return ({'message': f'User {username!r} does not exist'},
                    HTTP_NOT_FOUND)


class UserLogin(Resource):
    @staticmethod
    def post():
        data = _parser.parse_args()
        login_user = UserModel.find_by_username(data['username'])
        if login_user and safe_str_cmp(data['password'], login_user.password):

            refresh_token = create_refresh_token(login_user.id)
            refresh_jti = get_jti(refresh_token)
            # get the jti of refresh token so that it could
            # be linked to the access token as claim
            claims = {'refresh_jti': refresh_jti}

            access_token = create_access_token(identity=login_user.id,
                                               fresh=True,
                                               additional_claims=claims)
            event_detail = {'date': time()}
            produce_event(login_user.id, 'login', 'user', event_detail)
            return ({'access_token': access_token,
                     'refresh_token': refresh_token},
                    HTTP_OK)
        else:
            return ({'message': 'Authentication fail'},
                    HTTP_UNAUTHORIZED)


class UserLogout(Resource):
    @staticmethod
    @jwt_required()
    def post():
        # block the acccess token JWT uniqie identifier
        access_jti = get_jwt()['jti']
        blocklist.set(access_jti, '', ex=JWT_ACCESS_EXPIRES)
        # block the refresh token JWT uniqie identifier as well
        refresh_jti = get_jwt()['refresh_jti']
        blocklist.set(refresh_jti, '', ex=JWT_REFRESH_EXPIRES)

        event_detail = {'date': time()}
        produce_event(get_jwt_identity(), 'logout', 'user', event_detail)
        return {'message': 'Successfully logout'}, HTTP_OK


class UserTokenRefresh(Resource):
    @staticmethod
    @jwt_required(refresh=True)
    def post():
        # get the jti of refresh token to be linked to the
        # new non fresh token as claim
        refresh_jti = get_jwt()['jti']
        claims = {'refresh_jti': refresh_jti}

        target_user_id = get_jwt_identity()
        new_non_fresh_token = create_access_token(target_user_id,
                                                  fresh=False,
                                                  additional_claims=claims)
        return {'access_token': new_non_fresh_token}, HTTP_OK
