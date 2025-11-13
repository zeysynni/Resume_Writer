from agents import Agent, Tool, Runner, trace, Tool
from contextlib import AsyncExitStack
from agents.mcp import MCPServerStdio
from rich.markdown import Markdown
from rich.console import Console
import asyncio
from dotenv import load_dotenv

from templates import web_scraping_instructions
from mcp_params import web_scraping_mcp_params

load_dotenv(override=True)

async def get_web_scraping_agent(web_scraping_mcp_servers) -> Agent:
    web_scraping_agent = Agent(
        name="web_scraping_agent",
        instructions=web_scraping_instructions,
        mcp_servers=web_scraping_mcp_servers,
        model="gpt-4o-mini",
    )
    return web_scraping_agent

async def get_web_scraping_agent_tool(web_scraping_mcp_servers) -> Tool:
    web_scraping_agent = await get_web_scraping_agent(web_scraping_mcp_servers)
    return web_scraping_agent.as_tool(
            tool_name="web_scraping_agent_tool",
            tool_description="This tool allows you internet access, you can use it to search the web."
        )

async def run():
    async with AsyncExitStack() as stack:
        
        web_scraping_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in web_scraping_mcp_params]

        web_scraping_agent = await get_web_scraping_agent(web_scraping_servers)

        url = "https://join.vector.com/Germany/job/Stuttgart-Praktikum-Embedded-Software-Entwicklung-PythonC-%28mwd%29/301-de_DE/"
        message = f"The job URL is {url}, give me a summary of this job."

        with trace("test web scraping agent"):
            result = await Runner.run(web_scraping_agent, message, max_turns=10)
        #print(result.final_output) # if prefer desplay plain text
        console = Console()
        console.print(Markdown(result.final_output))


if __name__ == "__main__":
    asyncio.run(run())