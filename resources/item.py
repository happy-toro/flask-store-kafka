from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required,
                                get_jwt,
                                get_jwt_identity)

from resources.http_code import (HTTP_OK,
                                 HTTP_CREATED,
                                 HTTP_BAD_REQUEST,
                                 HTTP_UNAUTHORIZED,
                                 HTTP_NOT_FOUND)
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='Must spell the price for the item')
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Must spell the id of the store that this item belongs to')

    @staticmethod
    @jwt_required()
    def get(name):
        target_item = ItemModel.find_by_name(name)
        if target_item:
            return target_item.json(), HTTP_OK
        else:
            return ({'message': f'Item {name!r} does not exist'},
                    HTTP_NOT_FOUND)

    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return ({'message': f'Item {name!r} exists'},
                    HTTP_BAD_REQUEST)

        data = self.parser.parse_args()
        new_item = ItemModel(name, **data)
        new_item.save_to_db()
        return new_item.json(), HTTP_CREATED

    @classmethod
    @jwt_required(fresh=True)
    def put(cls, name):
        data = cls.parser.parse_args()
        target_item = ItemModel.find_by_name(name)
        if target_item:
            target_item.price = data['price']
            target_item.store_id = data['store_id']
            target_item.save_to_db()
            return target_item.json(), HTTP_OK
        else:
            new_item = ItemModel(name, **data)
            new_item.save_to_db()
            return new_item.json(), HTTP_CREATED

    @staticmethod
    @jwt_required(fresh=True)
    def delete(name):
        claims = get_jwt()
        if not claims['is_admin']:
            return ({'message': 'Admin privilege is required to delete item'},
                    HTTP_UNAUTHORIZED)

        target_item = ItemModel.find_by_name(name)
        if target_item:
            target_item.delete_from_db()
            return {'message': f'Item {name!r} is deleted'}, HTTP_OK
        else:
            return {'message': f'Item {name!r} does not exist'}, HTTP_NOT_FOUND


class ItemList(Resource):
    @staticmethod
    @jwt_required(optional=True)
    def get():
        if get_jwt_identity():
            return ({'items': [item.json() for item in ItemModel.find_all()]},
                    HTTP_OK)
        else:
            return ({'items': [{'name': item.name} for item in ItemModel.find_all()],
                    'message': 'Login to get more detail about the items'},
                    HTTP_OK)
