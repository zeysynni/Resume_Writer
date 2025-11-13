from agents import Agent, Tool, Runner, trace, Tool
from contextlib import AsyncExitStack
from agents.mcp import MCPServerStdio
from rich.markdown import Markdown
from rich.console import Console
import asyncio
from dotenv import load_dotenv

from templates import databank_management_instructions
from mcp_params import databank_management_mcp_params

load_dotenv(override=True)

async def get_databank_management_agent(databank_management_mcp_servers) -> Agent:
    databank_management_agent = Agent(
        name="databank_management_agent",
        instructions=databank_management_instructions,
        mcp_servers=databank_management_mcp_servers,
        model="gpt-4o-mini",
    )
    return databank_management_agent

async def get_databank_management_agent_tool(databank_management_mcp_servers) -> Tool:
    databank_management_agent = await get_databank_management_agent(databank_management_mcp_servers)
    return databank_management_agent.as_tool(
            tool_name="databank_management_agent_tool",
            tool_description="This tool manages a databank, it can save or retrieve usefull information from it."
        )

async def run():
    async with AsyncExitStack() as stack:
        
        databank_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in databank_management_mcp_params]

        databank_management_agent = await get_databank_management_agent(databank_servers)

        message = "What information do you have in your databank?"

        with trace("test databank management agent"):
            result = await Runner.run(databank_management_agent, message, max_turns=10)
        #print(result.final_output) # if prefer desplay plain text
        console = Console()
        console.print(Markdown(result.final_output))


if __name__ == "__main__":
    asyncio.run(run())