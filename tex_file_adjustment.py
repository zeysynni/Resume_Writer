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
            tool_description=(
                "Evaluate the quality of a LaTeX resume. "
                "Provide the FULL TEXT CONTENT of the .tex file as input (never the file path). "
                "The evaluator will return either APPROVED or REJECTED with actionable feedback. "
                "Use this tool after generating or revising a .tex file."
            )
    )

async def get_tex_writer_agent(tex_writer_mcp_servers, databank_management_mcp_servers) -> Agent:
    tex_writer_agent = Agent(
        name="tex_file_writer_agent",
        instructions=tex_writer_instructions(),
        mcp_servers=tex_writer_mcp_servers,
        tools=[await get_databank_management_agent_tool(databank_management_mcp_servers), tex_to_pdf, await get_tex_evaluator_agent_tool()],
        model="gpt-4o",
        handoff_description=(
            "You can read and write LaTeX files in the local './sandbox/Resume' directory. "
            "Your workflow is: (1) retrieve candidate/job info using databank tools, "
            "(2) read the LaTeX template, (3) generate a personalized .tex resume, "
            "(4) open the generated file and pass its *content* to your evaluation tool, "
            "(5) if the evaluation returns REJECTED, revise the .tex file and evaluate again "
            "until APPROVED, and (6) finally convert the approved .tex file to PDF using tex_to_pdf. "
            "Save both the final .tex and final .pdf inside './sandbox/Resume'."
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