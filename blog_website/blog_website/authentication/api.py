from ninja import Router, Form
from .schemas import UserSchema, UserTokenSchema
from .models import CustomUser
from blog_website.security import (BaseJWT, AuthTokenBearer)

from ninja.errors import HttpError
from django.db import IntegrityError
from datetime import datetime, timezone
auth_router = Router()

@auth_router.post("/register")
def register(request, payload: UserSchema):
    try:
        user = CustomUser.objects.create_user(**payload.dict())
        return {
            "status": "success",
            "data": {
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "phone": user.phone,
                "password": user.password
            }
        }
    except IntegrityError:
        return {"error": "User already exists"}
    


@auth_router.post("/login")
def login(request, payload: UserTokenSchema):
    try:
        user = CustomUser.objects.get(username=payload.username)
        if not user.check_password(payload.password):
            return {"error": "Invalid password"}
        return {
            "status": "Logged in",
            "user": user.username,
            "token": BaseJWT.get_token({"username": user.username,
                                        "password": user.password})  
        }
        
    except CustomUser.DoesNotExist:
        raise HttpError(404, "User not found")
    
   
@auth_router.get("/get-user-info", auth=AuthTokenBearer())
def get_user_info(request):
    token = request.headers.get('Authorization').split('Bearer ')[1]
    decoded = BaseJWT.get_info(token)
    username = decoded.get('username')
    user = CustomUser.objects.get(username=username)
    return {
        "status": "User found",
        "data":{
            "email": user.email,
            "exp": request.expire_datetime
        }
    }
    

