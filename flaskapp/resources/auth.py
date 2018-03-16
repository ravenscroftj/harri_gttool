"""Authentication resources"""

from flask_restful import Resource, reqparse, marshal_with, fields, reqparse, marshal
from flask_security import auth_token_required

class SecureResource(Resource):

    @auth_token_required
    def get(self):
        return {"message":"hello world"}
