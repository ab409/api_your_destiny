# app.py
import uvicorn
from fastapi import FastAPI

app = FastAPI()

from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def get_user():
    # 处理获取用户信息的请求
    return {"ID":1}

app.include_router(router)

if __name__ == '__main__':
	uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
