import jwt
from datetime import datetime, timedelta
key = 'jdasi@indada&nsadasd'
EXPIRE_TIME = 60*60*24*7
expire_datetime = datetime.now() + timedelta(seconds=EXPIRE_TIME)

class BaseJWT:
    @staticmethod
    def encode(payload):
        return jwt.encode({**payload,
                          'expire_datetime':expire_datetime.strftime('%Y-%m-%d %H:%M:%S')}, 
                          key, algorithm='HS512')
    
    @staticmethod
    def decode(token):
        return jwt.decode(token, key, algorithms='HS512')
    
    @staticmethod
    def get_token(token):
        return BaseJWT.encode(token)
    
    @staticmethod
    def get_info(token):
        if BaseJWT.check_expire(token):
            return BaseJWT.decode(token)
        return {}

    @staticmethod
    def check_expire(token):
        decoded = BaseJWT.decode(token)
        expire_datetime = datetime.strptime(decoded['expire_datetime'], '%Y-%m-%d %H:%M:%S')
        return expire_datetime > datetime.now()