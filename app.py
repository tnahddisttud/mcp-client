import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

st.set_page_config(page_title="HRMS Assistant", page_icon="🤖")
st.title("HRMS Assistant 🤖")

@st.cache_resource
def get_agent():
    async def _init():
        token = os.getenv("MCP_AUTH_TOKEN", "admin-token-123")
        client = MultiServerMCPClient(
            {
                "hrms": {
                    "transport": "http",
                    "url": "http://localhost:8080/mcp",
                    "headers": {
                        "Authorization": f"Bearer {token}"
                    }
                }
            }
        )
        tools = await client.get_tools()
        llm = ChatGroq(model="openai/gpt-oss-120b")
        agent = create_agent(llm, tools, checkpointer=InMemorySaver())
        return agent
    
    return asyncio.run(_init())

try:
    agent = get_agent()
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

config = {"configurable": {"thread_id": "hrms-session-streamlit"}}

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history on rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("How can I help you today?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            async def _invoke():
                return await agent.ainvoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config,
                )
            try:
                result = asyncio.run(_invoke())
                reply = result["messages"][-1].content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with agent: {e}")
