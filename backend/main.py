from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import listing, chat
from services.store import store
from core.config import settings
from contextlib import asynccontextmanager
import time
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database via the service
    await store.init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown logic could go here
    logger.info("Server shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Configuration: Optimized for Mobile Web Dev
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://localhost:.*", # More robust for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-API-Token"], # Explicitly allow our custom auth header
)

# Observability Middleware: Track Request Latency
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log the performance of the request
    logger.info(f"PATH: {request.url.path} | METHOD: {request.method} | LATENCY: {process_time:.4f}s")
    
    return response

# Include Routers
app.include_router(listing.router, prefix=f"{settings.API_V1_STR}/listing", tags=["listing"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} API is online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
