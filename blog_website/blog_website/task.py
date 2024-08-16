# blog_website/tasks.py

from celery import shared_task
from django.utils.text import slugify
import logging
from web_app.models import CustomUser

logger = logging.getLogger(__name__)

# @shared_task
# def create_post_task(post_data, user_id, file_url):
#     from web_app.models import CustomUser, Category, Post, Tag
    
#     logger.info(f"Processing task with data: {post_data.get('title')}")

#     try:
#         user = CustomUser.objects.get(id=user_id)
#         cate = Category.objects.get(id=post_data['category_id'])
        
#         logger.info(f"Creating post for user: {user.username}")
        
#         new_post = Post.objects.create(
#             title=post_data.get('title'),
#             content=post_data.get('content'),
#             slug=slugify(post_data.get('title')),
#             category=cate,
#             author=user,
#             is_published=post_data.get('is_published', False),
#             urlImage=file_url
#         )

#         for tag_data in post_data.get('tags', []):
#             tag, _ = Tag.objects.get_or_create(name=tag_data['name'], slug=slugify(tag_data['name']))
#             new_post.tags.add(tag)

#         logger.info(f"Post created: {new_post}")
#         return {'success': True}

#     except Exception as e:
#         logger.error(f"Error creating post: {e}")
#         raise
from django.utils.crypto import get_random_string
import string

@shared_task
def create_random_user_accounts(total):
    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        CustomUser.objects.create_user(username=username, email=email, password=password)
    return '{} random users created with success!'.format(total)