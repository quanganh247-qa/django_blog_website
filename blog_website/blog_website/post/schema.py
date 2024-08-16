from .models import Category,Post,Tag
from ninja import ModelSchema, Schema
from blog_website.category.schema import CategorySchema
from typing import List,Optional
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

class TagSchema(Schema):
    name: str
        
class PostSearchResultSchema(Schema):
    id: int
    title: str
    slug: str
    content: str
    author: str
    category: str
    # tags: List[TagSchema]
    created_at: str
    urlImage: Optional[str]  # Make urlImage optional
    

class CreatePostSchema(Schema):
    title: str
    content: str
    # category_id: int = None
    # tags: Optional[List[TagSchema]] = []
    
class UpdatePostSchema(Schema):
    title: str
    content: str
    category_id: Optional[int] = None
    tags: Optional[List[TagSchema]] = None
    is_published: bool = False
    remove: bool = False
    
class RemovePostSchema(Schema):
    remove: bool = True

@registry.register_document
class PostDocument(Document):
    
    id = fields.IntegerField(attr='id')
    slug = fields.KeywordField(attr='slug')
    content = fields.TextField(attr='content')
    created_at = fields.DateField(attr='created_at')
    updated_at = fields.DateField(attr='updated_at')
    is_published = fields.BooleanField(attr='is_published')
    urlImage = fields.TextField(attr='urlImage')
    remove = fields.BooleanField(attr='remove')
    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'slug': fields.TextField(),
    })
    
    author = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'username': fields.TextField(),
        'email': fields.TextField(),
        'full_name': fields.TextField(),
        'phone': fields.TextField(),
    })
    # tags = fields.NestedField(properties={
    #     'id': fields.IntegerField(),
    #     'name': fields.TextField(),
    #     'slug': fields.TextField(),
    # })
    
    title = fields.TextField(
        analyzer='standard',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
            # 'lower': fields.TextField(analyzer='lowercase')
        }
    )
    class Index:
        name = 'posts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            # 'analysis': {
            #     'analyzer': {
            #         'lowercase': {
            #             'type': 'custom',
            #             'tokenizer': 'standard',
            #             'filter': ['lowercase']
            #         }
            #     }
            # }
        }

    class Django:
        model = Post
        
        
