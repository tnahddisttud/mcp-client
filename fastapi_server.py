from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

MCP_SERVERS = {
    "hrms": {
        "transport": "stdio",
        "command": "python",
        "args": ["D:\\projects\\hr-assist\\server.py"],
        "env": {
            "CB_EMAIL": os.getenv("CB_EMAIL"),
            "CB_EMAIL_PWD": os.getenv("CB_EMAIL_PWD")
        }
    }
}

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    client = MultiServerMCPClient(MCP_SERVERS)
    tools = await client.get_tools()
    agent = create_agent(llm, tools, checkpointer=InMemorySaver())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config,
        )
        reply = result["messages"][-1].content
        return ChatResponse(response=reply)
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
