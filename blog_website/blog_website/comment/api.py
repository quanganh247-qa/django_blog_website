from ninja import Router,Schema, Form
from ninja.errors import HttpError
from blog_website.security import AuthTokenBearer
from django.db import transaction
from .models import *
from .schema import *
from typing import List
from django.db import IntegrityError
from ninja.pagination import paginate,LimitOffsetPagination
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from ..settings import CACHE_TTL
import logging

logger = logging.getLogger(__name__)
comment_router = Router()

@comment_router.get("/get-all-comments/{post_id}",response=List[CommentSchema], auth=AuthTokenBearer())
def get_all_comments(request, post_id: int):
    cache_key = f'all_comments_{post_id}'
    cache_data = cache.get(cache_key)
    post = get_object_or_404(Post, id=post_id, is_published=True, remove=False)
    if post is None:
        raise HttpError(404, "Post not found")
    if cache_data is None:
        results = Comment.objects.filter(Q(post=post) & Q(is_approved=True))
        serizialed_results = [
            {
                "id": comment.id,
                "post_id": comment.post.id,
                "author": comment.author.username,
                "content": comment.content,
            } 
            for comment in results
        ]
        cache.set(cache_key, serizialed_results, timeout=CACHE_TTL)
        return serizialed_results
    return cache_data

@comment_router.post("/create-comment/{post_id}", auth=AuthTokenBearer())
def create_comment(request, data:CreateCommentSchema, post_id:str):
    post = get_object_or_404(Post, id=post_id, is_published=True, remove=False)
    if post is None:
        raise HttpError(404, "Post not found")
    try:
        Comment.objects.create(
            post = post,
            author = request.user,
            content = data.content,
            is_approved = True
        )
        cache.clear()
    except IntegrityError:
        raise HttpError(400, "Comment already exists")
    return {
        'success': True,
    }
    
@transaction.atomic
@comment_router.put("/update-comment/{comment_id}", response=CommentSchema, auth=AuthTokenBearer())
def update_comment(request, comment_id: int, data: Form[UpdateCommentSchema]):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.content = data.content
        comment.save()
        return comment
    except Comment.DoesNotExist:
        raise HttpError(404, "Comment not found")
    
@comment_router.get("/sort-comments-desc/{post_slug}",response=List[CommentSchema], auth=AuthTokenBearer())
def desc_sort_comments(request, post_slug: str):
    cache_key = f'sort_comments_desc_{post_slug}'
    cache_data = cache.get(cache_key)
    if cache_data is None:
        post = get_object_or_404(Post, slug=post_slug, is_published=True, remove=False)
        if post is None:
            raise HttpError(404, "Post not found")
        comments = Comment.objects.filter(Q(post=post) & Q(is_approved=True)).order_by('-created_at')
        return comments
    return cache_data

@comment_router.get("/sort-comments-asc/{post_slug}",response=List[CommentSchema], auth=AuthTokenBearer())
def asc_sort_comments(request, post_slug: str):
    cache_key = f'sort_comments_asc_{post_slug}'
    cache_data = cache.get(cache_key)
    if not cache_data:
        post = get_object_or_404(Post, slug=post_slug, is_published=True, remove=False)
        if post is None:
            raise HttpError(404, "Post not found")
        comments = Comment.objects.filter(Q(post=post) & Q(is_approved=True)).order_by('created_at')
        return comments
    
    return cache_data