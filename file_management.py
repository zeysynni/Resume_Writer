import easyocr
from pdf2image import convert_from_path
import numpy as np
from agents import Agent, function_tool, Runner, trace, Tool
from contextlib import AsyncExitStack
from agents.mcp import MCPServerStdio
from rich.markdown import Markdown
from rich.console import Console
import asyncio
from dotenv import load_dotenv

from templates import read_resume_instructions, file_management_instructions
from resume_structure import Resume
from mcp_params import file_management_mcp_params

load_dotenv(override=True)

@function_tool
async def read_pdf(pdf_path: str) -> str:
    """ Given the path of a PDF, convert it into a raw string. """
    pages = convert_from_path(pdf_path)
    reader = easyocr.Reader(['en', 'de']) 
    text = ""
    for page in pages:
        text += "\n".join(reader.readtext(np.array(page), detail=0))
    return f"The complete content from the PDF file is: {text}."

async def get_read_resume_agent() -> Agent:
    read_resume_agent = Agent(
        name="read_resume_agent",
        instructions=read_resume_instructions,
        tools=[read_pdf],
        model="gpt-4o-mini",
        output_type=Resume,
    )
    return read_resume_agent

async def get_read_resume_agent_tool() -> Tool:
    read_resume_agent = await get_read_resume_agent()
    return read_resume_agent.as_tool(
            tool_name="read_resume_agent_tool",
            tool_description="Use this tool read a PDF file, e.g. a resume, and output a summary for it."
        )

async def get_file_management_agent(file_management_mcp_servers) -> Agent:
    file_management_agent = Agent(
        name="file_management_agent",
        instructions=file_management_instructions,
        tools=[await get_read_resume_agent_tool()],
        mcp_servers=file_management_mcp_servers,
        model="gpt-4o-mini",
    )
    return file_management_agent

async def get_file_management_agent_tool(file_management_mcp_servers) -> Tool:
    file_management_agent = await get_file_management_agent(file_management_mcp_servers)
    return file_management_agent.as_tool(
            tool_name="file_management_agent_tool",
            tool_description=(
                "Use this tool to read, list, and summarize files inside the './sandbox' directory. "
                "It is especially useful for reading resumes (PDFs) or LaTeX files before processing them."
            )
        )

async def run():
    async with AsyncExitStack() as stack:

        file_servers = [await stack.enter_async_context(MCPServerStdio(params)) for params in file_management_mcp_params]

        file_management_agent = await get_file_management_agent(file_servers)

        message = "Tell me the only name of files you have, no need to tell me anything about the content, only file names."
        cv_path = "Lebenslauf_ZeyuanSun.pdf"
        message = f"The candidate's old resume is {cv_path}, see if you can read and understand it."

        with trace("test file management agent"):
            result = await Runner.run(file_management_agent, message, max_turns=10)
        #print(result.final_output) # if prefer desplay plain text
        console = Console()
        console.print(Markdown(result.final_output))


if __name__ == "__main__":
    asyncio.run(run())