from contextlib import AsyncExitStack
from agents import Agent, Runner, trace, Tool
from IPython.display import Markdown
import asyncio
from rich.markdown import Markdown
from rich.console import Console

from agents.mcp import MCPServerStdio

from templates import tex_writer_instructions, evaluator_instructions
from databank_management import get_databank_management_agent_tool
from tools import tex_to_pdf
from mcp_params import files_params, memory_params

async def get_tex_evaluator_agent() -> Agent:
    tex_evaluator_agent = Agent(
        name="tex_evaluator_agent",
        instructions=evaluator_instructions,
        model="gpt-4o",
    )
    return tex_evaluator_agent

async def get_tex_evaluator_agent_tool() -> Tool:
    tex_evaluator_agent = await get_tex_evaluator_agent()
    return tex_evaluator_agent.as_tool(
            tool_name="evaluate_tex_file",
            tool_description="Use this tool to evaluate a LaTeX document you have written and get feedback on its quality.\
                Provide the text content of the .tex file as input, NOT the file path."
    )

async def get_tex_writer_agent(tex_writer_mcp_servers, databank_management_mcp_servers) -> Agent:
    tex_writer_agent = Agent(
        name="tex_file_writer_agent",
        instructions=tex_writer_instructions(),
        mcp_servers=tex_writer_mcp_servers,
        tools=[await get_databank_management_agent_tool(databank_management_mcp_servers), tex_to_pdf, await get_tex_evaluator_agent_tool()],
        model="gpt-4o",
        handoff_description=(
            "You are able to read and write files in your local directory, especially .tex files. "
            "After writing the resume .tex file, open it and read its content. "
            "Then call your 'evaluate_tex_content' tool, passing the text content (not the file path). "
            "If the evaluation result says REJECTED, revise the .tex file accordingly and try again."
            "After you have finished, save your work both as PDF and as .tex file. Tell the user where are they saved."
        )
    )
    return tex_writer_agent

async def run():
    async with AsyncExitStack() as stack:
        tex_writer_mcp_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in [files_params]]
        databank_management_mcp_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in [memory_params]]

        tex_writer_agent = await get_tex_writer_agent(tex_writer_mcp_servers, databank_management_mcp_servers)

        message = "Retrieve your databank for job and candidate information, then write me a new resume."

        with trace("test tex writer agent"):
            result = await Runner.run(tex_writer_agent, message, max_turns=20)
        #print(result.final_output) # if prefer desplay plain text
        console = Console()
        console.print(Markdown(result.final_output))


if __name__ == "__main__":
    asyncio.run(run())