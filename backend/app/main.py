from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, api_keys, publishing, articles, articles_generate
from app.core.config import settings

app = FastAPI(
    title="WritAi API",
    description="AI Writing & SEO Suite API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(api_keys.router, prefix="/api/v1/api-keys", tags=["api-keys"])
app.include_router(publishing.router, prefix="/api/v1/publishing", tags=["publishing"])
app.include_router(articles.router, prefix="/api/v1/articles", tags=["articles"])
app.include_router(articles_generate.router, prefix="/api/v1/articles", tags=["articles"])


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
