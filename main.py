import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


async def main():
    client = MultiServerMCPClient(
        {
            "hrms": {
                "transport": "stdio",
                "command": "python",
                "args": ["D:\\projects\\hr-assist\\server.py"],
            }
        }
    )
    tools = await client.get_tools()

    llm = ChatGroq(model="llama-3.3-70b-versatile")
    agent = create_agent(llm, tools, checkpointer=InMemorySaver())

    config = {"configurable": {"thread_id": "hrms-session"}}

    print("HRMS Assistant (type 'exit' to quit)")
    print("-" * 40)

    while True:
        prompt = input("\nYou: ").strip()
        if not prompt:
            continue
        if prompt.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config,
        )
        reply = result["messages"][-1].content
        print(f"\nAssistant: {reply}")


if __name__ == "__main__":
    asyncio.run(main())