from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router

app = FastAPI(
    title="He Thong Dao Tao CodeGym",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Gắn API login
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Backend đang hoạt động"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }