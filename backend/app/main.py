from fastapi import FastAPI

app = FastAPI(title="He Thong Dao Tao CodeGym")


@app.get("/")
def home():
    return {"message": "Backend đang hoạt động"}