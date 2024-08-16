# Blog Website Backend

This is the backend for a blog website built using Django Ninja, Redis for caching, and Elasticsearch for search functionality.

## Prerequisites

- Python 3.x
- Django
- Django Ninja
- Redis
- Elasticsearch

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/blog-website-backend.git
    cd blog-website-backend
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    venv\Scripts\activate  # On Windows
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up Redis and Elasticsearch on your local machine or use hosted services.

## Running the Application

1. Set the Django settings module:
    ```sh
    set DJANGO_SETTINGS_MODULE=blog_website.settings  # On Windows
    ```

2. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Technologies Used

- **Django**: A high-level Python web framework.
- **Django Ninja**: A web framework for building APIs with Django and Python 3.6+ type hints.
- **Redis**: An in-memory data structure store, used as a database, cache, and message broker.
- **Elasticsearch**: A distributed, RESTful search and analytics engine.

## API Documentation

The API is built using Django Ninja. You can access the API documentation at: http://127.0.0.1:8000/api/docs


## Caching with Redis

Redis is used to cache frequently accessed data to improve performance. Ensure Redis is running and configured in your Django settings.

## Search with Elasticsearch

Elasticsearch is used to provide advanced search capabilities. Ensure Elasticsearch is running and configured in your Django settings.
