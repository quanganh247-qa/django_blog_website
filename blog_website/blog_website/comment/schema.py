from .models import *
from ninja import Schema
from datetime import datetime 
from typing import List, Optional

class CommentSchema(Schema):
    id : int
    post_id: int
    author: str
    content: str
    
class CreateCommentSchema(Schema):
    content: str
    
class UpdateCommentSchema(Schema):
    content: str
    updated_at: str = None
