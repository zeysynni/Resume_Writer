import asyncio
from IPython.display import Markdown
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from contextlib import AsyncExitStack
from rich.markdown import Markdown
from rich.console import Console

from file_management import get_file_management_agent_tool
from web_scraping import get_web_scraping_agent_tool
from databank_management import get_databank_management_agent_tool
from tex_file_adjustment import get_tex_writer_agent
from templates import manager_instructions

from mcp_params import file_management_mcp_params, web_scraping_mcp_params, databank_management_mcp_params, tex_writer_mcp_params

load_dotenv(override=True)

async def create_mcp_servers(stack: AsyncExitStack):
        file_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in file_management_mcp_params]
        web_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in web_scraping_mcp_params]
        databank_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in databank_management_mcp_params]
        tex_writer_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in tex_writer_mcp_params]
        return file_servers, web_servers, databank_servers, tex_writer_servers

async def create_manager_agent(stack: AsyncExitStack) -> Agent:
    file_servers, web_servers, databank_servers, tex_writer_servers = await create_mcp_servers(stack)

    file_tool = await get_file_management_agent_tool(file_servers)
    web_tool = await get_web_scraping_agent_tool(web_servers)
    databank_tool = await get_databank_management_agent_tool(databank_servers)
    tex_writer_agent = await get_tex_writer_agent(tex_writer_servers, databank_servers)

    manager = Agent(
        name="Manager",
        instructions=manager_instructions,
        tools=[file_tool, web_tool, databank_tool],
        handoffs=[tex_writer_agent],
        model="gpt-4o-mini"
    )

    return manager

async def chat_with_agent(manager: Agent, message = "The candidate's old resume is Lebenslauf_ZS.pdf, the job URL is https://join.vector.com/"):
        with trace("Automated Resume Writer Test"):
            result = await Runner.run(manager, message, max_turns=10)
        print("\n=== Final Output ===")
        #print(result.final_output or "⚠️ No valid output returned.") # if prefer desplay plain text
        console = Console()
        console.print(Markdown(result.final_output))

async def main():
        async with AsyncExitStack() as stack:
            manager = await create_manager_agent(stack)
            await chat_with_agent(manager)

if __name__ == "__main__":
    asyncio.run(main())

