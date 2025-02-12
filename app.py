import httpx
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
timeout = httpx.Timeout(timeout=5.0, read=15.0)
client = httpx.AsyncClient(limits=limits, timeout=timeout)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                # 设置接收超时
                username = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60  # 60秒超时
                )
                user = await get_github_profile(None, username)
                if user:
                    await websocket.send_json(user.dict())
                else:
                    await websocket.send_json({"error": "User not found"})
                
                # 发送心跳
                await websocket.send_json({"type": "ping"})
                
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                continue
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


@app.on_event("shutdown")
async def shutdown_event():
    print("shutting down...")
    await client.aclose()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, username: str = None):
    if not username:
        return templates.TemplateResponse("index.html", context={"request": request})

    user = await get_github_profile(request, username)
    if not user:
        return templates.TemplateResponse("404.html", context={"request": request})

    return templates.TemplateResponse("index.html", context={"request": request, "user": user})