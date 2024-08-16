from django.contrib import admin

# Register your models here.
from .models import Category, Tag, Post, Comment, CustomUser

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

admin.site.register(CustomUser)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)