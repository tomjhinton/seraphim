from datetime import datetime, timedelta
import jwt
import bcrypt

from pony.orm import Required, Set, Optional
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from app import db
from config.environment import secret


class User(db.Entity):
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    password_hash = Required(str)




    def is_password_valid(self, plaintext):
        return bcrypt.checkpw(plaintext.encode('utf8'), self.password_hash.encode('utf8'))

    def generate_token(self):
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=6),
            'iat': datetime.utcnow(),
            'sub': self.id
        }

        token = jwt.encode(
            payload,
            secret,
            'HS256'
        ).decode('utf8')

        return token
    ##following






class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(load_only=True)
    password_confirmation = fields.Str(load_only=True)




    # basic method
    def generate_hash(self, plaintext):
        return bcrypt.hashpw(plaintext.encode('utf8'), bcrypt.gensalt(8)).decode('utf8')

    # validate schema allows for custom error messages
    @validates_schema
    def check_passwords(self, data, **kwargs):
        if data['password'] and data['password'] != data['password_confirmation']:
            raise ValidationError(
                field_name='password_confirmation',
                message=['Does not match']
            )


    @validates_schema
    def validate_username(self, data, **kwargs):
        user = User.get(username=data.get('username'))

        if user:
            raise ValidationError(
                field_name='username',
                message=['Must be unique']
            )


    @validates_schema
    def validate_email(self, data, **kwargs):
        user = User.get(email=data.get('email'))

        if user:
            raise ValidationError(
                field_name='email',
                message=['Must be unique']
            )


    # logic to perform AFTER validation but before save, to modify the data
    @post_load
    def hash_password(self, data, **kwargs):
        if data['password']:
            data['password_hash'] = self.generate_hash(data['password'])

            del data['password']
            del data['password_confirmation']

        return data
