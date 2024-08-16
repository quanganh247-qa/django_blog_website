from .models import *
from ninja import Form, File,Router, UploadedFile
from ninja.errors import HttpError
from .schema import *
from ninja.pagination import paginate,LimitOffsetPagination
from blog_website.security import (BaseJWT, AuthTokenBearer)
from elasticsearch_dsl import Search,Q
from elasticsearch_dsl.query import Bool, Match, Term
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.text import slugify
from django.db import transaction
from ..settings import CACHE_TTL, AWS_SECRET_ACCESS_KEY,AWS_ACCESS_KEY_ID,AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME
import boto3
from botocore.exceptions import NoCredentialsError
from django.core.cache import cache
from blog_website.task import create_random_user_accounts

import logging

logger = logging.getLogger(__name__)

post_router = Router()

@post_router.get("/get-all-posts",response=List[PostSearchResultSchema], auth=AuthTokenBearer())
@paginate(LimitOffsetPagination)
def get_all_posts(request):
    cache_key = 'all_posts'
    posts = cache.get(cache_key)

    if posts is None:
        posts = list(Post.objects.filter(is_published=True, remove=False))
        serialized_posts = [
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "content": post.content,
                "author": post.author.username,
                "category": post.category.name,
                # "tags": [{"name": tag.name} for tag in post.tags.all()],
                "created_at": post.created_at.isoformat(),
                "urlImage": post.urlImage or None,
            } 
            for post in posts
        ]
        cache.set(cache_key, serialized_posts, timeout=CACHE_TTL)
    else:
        serialized_posts = posts
    return serialized_posts


@post_router.get("/get-post",response=PostSearchResultSchema, auth=AuthTokenBearer())
def get_post(request, post_id: int):
    cache_key = f'post_{post_id}'
    cache_data =  cache.get(cache_key)
    result = None
    if cache_data is None:
        try:
            post = Post.objects.get(id=post_id)
            result = PostSearchResultSchema(
                id=post.id,
                title=post.title,
                slug=post.slug,
                content=post.content,
                author=post.author.username,
                category=post.category.name,
                # tags=[TagSchema(name=tag.name) for tag in post.tags.all()],
                created_at=post.created_at.isoformat(),
                urlImage=post.urlImage or None,
            )
            return result
        except Post.DoesNotExist:
            raise HttpError(404, "Post not found")
    else:
        result = cache_data
    return result
    
    
@post_router.get("/search", response=List[PostSearchResultSchema], auth=AuthTokenBearer())
def search_posts(request, name: str):   

    cache_key = f'search_{name}'
    cache_data = cache.get(cache_key)
    results = []
    
    if cache_data is None:
        query = Q(
            "bool",
            must=[
                Q("match_phrase_prefix", title={"query": name, "slop": 2}),  # Better for partial matching
                Q("term", is_published=True),  # Ensure only published posts are returned
                Q("term", remove=False)  # Ensure only posts where remove is False
            ]
        )

        s = Search(index='posts').query(query).sort('-created_at')
        response = s.execute()
    
        for hit in response:
            results.append(
                PostSearchResultSchema(
                    id=hit.id,
                    title=hit.title,
                    slug=hit.slug,
                    content=hit.content,
                    author=hit.author.username,
                    category=hit.category.name,
                    created_at=hit.created_at.format(),
                    urlImage=hit.urlImage or None,
                )
            )
        cache.set(cache_key, results, timeout=CACHE_TTL)
        return results
    else:
        results = cache_data
    return results


@post_router.post("/create-post", auth=AuthTokenBearer())
def create_post(request, 
                 title: str = Form(...),
                 content: str = Form(...),
                 file: UploadedFile = File(...)):

    # Upload image to S3
    file_url = upload_img_S3(file, AWS_STORAGE_BUCKET_NAME)

    # Validate or get the category
    category = get_object_or_404(Category, id=1)

    # Create the post instance
    post = Post.objects.create(
        title=title,
        content=content,
        slug = slugify(title),
        author = request.user,
        category=category,
        urlImage=file_url
    )

    cache.clear()

    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'urlImage': post.urlImage,
    }
        
def upload_img_S3(file: File[UploadedFile],bucket_name, object_name=None):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME,
    )
    try:
        if object_name is None:
            object_name = file.name

        # Upload the file to S3
        s3_client.upload_fileobj(file, bucket_name, object_name)

        url = f"https://{bucket_name}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{object_name}"
        
        return url
    except NoCredentialsError:
        print("Credentials not available")
        return None
        
@transaction.atomic
@post_router.put("/update-post/{post_id}", response=PostSearchResultSchema, auth=AuthTokenBearer())
def edit_post(request, post_id: int, post_data: UpdatePostSchema):
    post = get_object_or_404(Post, id=post_id)
    if post:
        
        post.title = post_data.title if post_data.title else post.title
        post.content = post_data.content if post_data.content else post.content
        post.slug = slugify(post_data.title) if post_data.title else post.slug
        post.category_id = post_data.category_id if post_data.category_id else post.category
        post.is_published = post_data.is_published if post_data.is_published else post.is_published
        # post.tags = None
        post.save()
        
        if post.tags:
            # Update tags
            tags = post.tags.all()
            for tag in tags:
                post.tags.set([])
            
            for tag_data in post_data.tags:
                tag, created = Tag.objects.get_or_create(name=tag_data.name, slug=slugify(tag_data.name))
                post.tags.add(tag)
                
        
        post_document = PostDocument.get(id=post.id)
        post_document.update(post)
    
        post.save()
        cache.delete_pattern('all_posts_*')
        
        response_data = PostSearchResultSchema(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            category_id=post.category_id,
            tags=[TagSchema(name=tag.name) for tag in post.tags.all()],
            is_published=post.is_published,
            created_at=post.created_at.isoformat(),
            updated_at=post.updated_at.isoformat(),
            urlImage=post.urlImage or None,
        )

        return response_data
    else:
        raise HttpError(404, "Post not found")
    
@post_router.put("/remove-post/{post_id}", auth=AuthTokenBearer())
def delete_post(request, post_id: int, post_data: RemovePostSchema):
    post = get_object_or_404(Post, id=post_id)
    if post:
        post.remove = post_data.remove if post_data.remove else post.remove
        cache.delete_pattern('all_posts_*')
        return {"status": "success",}
    else:
        raise HttpError(404, "Post not found")
    

# @post_router.post("/create-post")
# def create_post(request, post_data: CreatePostSchema, file: File[UploadedFile]):
#     # Upload image to S3
#     url = upload_img_S3(file, AWS_STORAGE_BUCKET_NAME)
    
#     # Prepare data for Celery task
#     task_data = {
#         'title': post_data.title,
#         'content': post_data.content,
#         'category_id': post_data.category_id,
#         'tags': [{'name': tag.name} for tag in post_data.tags],
#         'is_published': post_data.is_published
#     }

#     # new_p = create_post_task.apply_async(args=[task_data, request.user.id, url], queue='blog_queue')
#     # new_p = create_post_task.delay(task_data, request.user.id, url)
#     new_p = test_post_task.delay(2,3)

#     # Clear cache
#     cache.delete_pattern('all_posts_*')
#     cache.delete_pattern('search_*')
#     cache.delete_pattern('post_*')

#     return {"status": "success"}
        