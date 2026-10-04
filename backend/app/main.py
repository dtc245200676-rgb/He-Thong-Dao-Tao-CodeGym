from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth_router, roles_router, users_router
from app.db.database import SessionLocal
from app.db.seed import seed_rbac


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = SessionLocal()
    try:
        seed_rbac(db)
    except Exception as exc:
        # The database may not be migrated yet on the very first run.
        # Keep the error visible without hiding the API startup diagnostics.
        print(f"[startup] Chưa thể seed RBAC: {exc}")
        db.rollback()
    finally:
        db.close()
    yield


app = FastAPI(
    title="He Thong Dao Tao CodeGym",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)


@app.get("/")
def home():
    return {"message": "Backend đang hoạt động", "sprint": "Sprint 1"}


@app.get("/health")
def health():
    return {"status": "ok"}
