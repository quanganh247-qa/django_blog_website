from ninja import ModelSchema
from .models import Category

class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"