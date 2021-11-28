from flask_restful import Resource
from flask_jwt_extended import (jwt_required,
                                get_jwt,
                                get_jwt_identity)
from requests.sessions import session

from resources.http_code import (HTTP_OK,
                                 HTTP_CREATED,
                                 HTTP_BAD_REQUEST,
                                 HTTP_UNAUTHORIZED,
                                 HTTP_NOT_FOUND)
from models.store import StoreModel
from outbox import produce_event


class Store(Resource):
    @jwt_required()
    def get(self, name):
        target_store = StoreModel.find_by_name(name)
        if target_store:
            return target_store.json(), HTTP_OK
        else:
            return ({'message': f'Store {name!r} does not exist'},
                    HTTP_NOT_FOUND)

    @staticmethod
    @jwt_required(fresh=True)
    def post(name):
        if StoreModel.find_by_name(name):
            return ({'message': f'Store {name!r} exists'},
                    HTTP_BAD_REQUEST)

        new_store = StoreModel(name)
        new_store.save_to_db()
        produce_event(get_jwt_identity(), 'create', 'store', new_store.json())
        return new_store.json(), HTTP_CREATED

    @staticmethod
    @jwt_required(fresh=True)
    def delete(name):
        claims = get_jwt()
        if not claims['is_admin']:
            return ({'message': 'Admin privilege is required to delete store'},
                    HTTP_UNAUTHORIZED)

        target_store = StoreModel.find_by_name(name)
        if target_store:
            event_value = target_store.json()
            target_store.delete_from_db()
            produce_event(get_jwt_identity(), 'delete', 'store', event_value)
            return {'message': f'Store {name!r} is deleted'}, HTTP_OK
        else:
            return {'message': f'Store {name!r} does not exist'}, HTTP_NOT_FOUND


class StoreList(Resource):
    @staticmethod
    @jwt_required(optional=True)
    def get():
        user_id = get_jwt_identity()
        produce_event(user_id, 'list', 'store', {})
        if user_id:
            return ({'stores': [store.json() for store in StoreModel.find_all()]},
                    HTTP_OK)
        else:
            return ({'stores': [{'name': store.name} for store in StoreModel.find_all()],
                     'message': 'Login to get more detail about the stores'},
                    HTTP_OK)
