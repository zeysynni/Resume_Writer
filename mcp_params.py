import os

sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))

files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}
memory_params = {"command": "npx","args": ["-y", "mcp-memory-libsql"],"env": {"LIBSQL_URL": "file:./memory/candidate.db"}}
playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}

file_management_mcp_params = [files_params]

web_scraping_mcp_params = [playwright_params]

databank_management_mcp_params = [memory_params]

tex_writer_mcp_params = [files_params]
