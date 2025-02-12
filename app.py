# app.py
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi import APIRouter

app = FastAPI()
router = APIRouter()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@router.get('/')
async def get_user():
    # 处理获取用户信息的请求
    return {"ID":1}

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
