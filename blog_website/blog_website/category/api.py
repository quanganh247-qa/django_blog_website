from ninja import Router
from ninja.errors import HttpError
from django.db import IntegrityError
from datetime import datetime, timezone
from .models import Category
from .schema import CategorySchema
from ninja.pagination import paginate,LimitOffsetPagination
from blog_website.security import (BaseJWT, AuthTokenBearer)
from typing import List

cat_router = Router()

@cat_router.get("/get-all-categories",response=List[CategorySchema], auth=AuthTokenBearer())
@paginate(LimitOffsetPagination)
def get_all_categories(request):
    return Category.objects.all()

@cat_router.get("/get-category/{category_slug}",response=CategorySchema, auth=AuthTokenBearer())
def get_cat_by_slug(request,category_slug:str):
    try:
        return Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        raise HttpError(404, "Category not found")