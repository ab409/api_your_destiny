# app.py
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi import APIRouter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
from langchain.chat_models import ChatZhipuAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import SystemMessage, HumanMessage, AIMessage

app = FastAPI()
router = APIRouter()

llm = ChatZhipuAI(model_name="glm-4-flash", streaming=True, zhipuai_api_key="")

# 创建提示模板
prompt = PromptTemplate(
    input_variables=["question"],
    template="请回答下面的问题：{question}"
)

# 定义不同助手的系统消息
ASSISTANT_CONFIGS = {
    "1": "你的名字是百晓生，是一位专业的算命先生，擅长解答算命、算凶吉、起名、看风水等相关问题。",
    "2": "你是一位专业的数学老师，擅长解答数学问题。",
    "3": "你是一位专业的英语教师，擅长英语教学和翻译。",
    "4": "你是一位专业的心理咨询师，擅长倾听和提供建议。",
    "5": "你是一位专业的职业规划顾问，擅长提供职业发展建议。",
    "6": "你是一位专业的生活助手，擅长解答日常生活问题。"
}

# Replace LLMChain with RunnableSequence
chain = prompt | llm

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                messages = data.get('messages', [])
                assistant_id = str(data.get('assistantId'))
                
                if assistant_id not in ASSISTANT_CONFIGS:
                    raise ValueError("Invalid assistant ID")

                # 构建消息列表
                chat_messages = []
                
                # 添加系统消息
                chat_messages.append(SystemMessage(content=ASSISTANT_CONFIGS[assistant_id]))
                
                # 添加对话历史
                for msg in messages:
                    if msg["role"] == "user":
                        chat_messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        chat_messages.append(AIMessage(content=msg["content"]))
                
                print(f"Processing messages with assistant {assistant_id}")
                
                # 使用新的消息列表进行对话
                async for chunk in llm.astream(chat_messages):
                    print(chunk)
                    if hasattr(chunk, 'content'):
                        await websocket.send_text(chunk.content)
                await websocket.send_text("[DONE]")
                
            except json.JSONDecodeError as e:
                await websocket.send_text(f"Error: Invalid JSON format - {str(e)}")
            except Exception as e:
                print(f"Error: {str(e)}")
                await websocket.send_text(f"Error: {str(e)}")
                
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
