# CORS_ORIGINS_WHITELIST = (
#   'http://localhost:3000',
# )

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Add your frontend URL here
    "http://127.0.0.1:3000",  # Add other allowed origins if necessary
]
CORS_ALLOW_METHODS = (
  'GET',
  'POST',
  'PUT',
  'DELETE',
  'OPTIONS',
)

CORS_ALLOW_HEADERS = (
  'accept',
  'accept-encoding',
  "content-type",
  "authorization",
  'x-csrftoken',
  'x-requested-with',
)