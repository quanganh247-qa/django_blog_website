from ninja import Schema, ModelSchema
from .models import CustomUser
class UserSchema(ModelSchema):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password', 'username', 'full_name']
        
class UserTokenSchema(Schema):
    username: str
    password: str   