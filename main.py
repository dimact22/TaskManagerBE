from fastapi import FastAPI
import cProfile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import OpenAPI
from logger import logger
from memory_profiler import profile
from fastapi.openapi.utils import get_openapi
from routes.users import user_app as users  # Import the correct router object

profiler = cProfile.Profile()
profiler.enable()
# Initialize FastAPI app
app = FastAPI()
@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi():
    return get_openapi(
        title="My API",
        version="1.0.0",
        description="Custom description of my API",
        routes=app.routes,
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down...")
    profiler.disable()
    profiler.dump_stats("profile_results.prof")
    
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
