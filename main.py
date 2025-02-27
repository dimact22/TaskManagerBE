from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.users import user_app as users  # Import the correct router object

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Include the `users` router
app.include_router(users)
