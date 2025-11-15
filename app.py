import gradio as gr
import json, os, shutil
from agents import Runner, trace
from contextlib import AsyncExitStack

from manager import create_manager_agent

HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

async def chat_with_agent(message, chat_history, file, url, tex_file):
    chat_history = chat_history or load_history()

    context = ""
    if url:
        context += f"\nThe user provided a job URL: {url}"
    if file:
        sandbox_path = os.path.join(os.getcwd(), "sandbox")
        os.makedirs(sandbox_path, exist_ok=True)
        dest_path = os.path.join(sandbox_path, os.path.basename(file.name))
        shutil.copy(file.name, dest_path)
        context += f"\nThe user uploaded a file saved at: {dest_path}"
    if tex_file:
        sandbox_path = os.path.join(os.getcwd(), "sandbox")
        os.makedirs(sandbox_path, exist_ok=True)
        dest_path = os.path.join(sandbox_path, os.path.basename(tex_file.name))
        shutil.copy(tex_file.name, dest_path)
        context += f"\nThe user uploaded a LaTeX template saved at: {dest_path}"

    chat_history.append({"role": "user", "content": message + context})

    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history
    )

    async with AsyncExitStack() as stack:
        manager = await create_manager_agent(stack)
        with trace("Automated Resume writer"):
            result = await Runner.run(manager, history_text, max_turns=10)

            reply = result.final_output
            chat_history.append({"role": "assistant", "content": reply})
            save_history(chat_history)

    return chat_history, "", None, "", None

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    return None


with gr.Blocks() as demo:
    gr.Markdown("## 💬 Persistent Resume Assistant")

    with gr.Row():
        url_input = gr.Textbox(label="Job URL", placeholder="Paste job posting URL...")
        file_input = gr.File(label="Upload your Resume (PDF)", file_types=[".pdf"])
        tex_input = gr.File(
            label="Upload LaTeX Template (.tex)",
            file_types=[".tex"]
            )

    chatbot = gr.Chatbot(type="messages", value=load_history(), height=400)
    msg = gr.Textbox(label="Your message")
    clear = gr.Button("Clear History")

    msg.submit(chat_with_agent, [msg, chatbot, file_input, url_input, tex_input], [chatbot, msg, file_input, url_input, tex_input])
    clear.click(clear_history, None, chatbot, queue=False)

demo.launch(share=True)