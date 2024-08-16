

from django.contrib import admin
from django.urls import path, include
from ninja import NinjaAPI
from blog_website.authentication.api import auth_router
from blog_website.category.api import cat_router
from blog_website.post.api import post_router
from blog_website.comment.api import comment_router
import debug_toolbar
api = NinjaAPI()

api.add_router("/auth", auth_router)
api.add_router("/category", cat_router)
api.add_router("/post", post_router)
api.add_router("/comment", comment_router)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', api.urls),
     path('__debug__/', include(debug_toolbar.urls))

]
