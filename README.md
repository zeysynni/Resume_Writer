# 🧠 Automated Resume Assistant

This project is an **AI-powered resume assistant** built with the [OpenAI Agent SDK](https://github.com/openai/agents), capable of:
- Scraping job postings,
- Managing user data,
- Writing LaTeX-based resumes,
- Evaluating resume quality using an LLM evaluator,
- And exporting final resumes as PDF.

It combines multiple specialized agents communicating via **MCP servers** and runs with a simple **Gradio web UI**.

---

## 🚀 Features

- **`Manager Agent`** — coordinates the workflow between specialized agents.  
- **`Web Scraping Agent`** — fetches job postings and extracts relevant content.  
- **`Databank Agent`** — stores and retrieves candidate/job data.  
- **`TeX Writer Agent`** — generates `.tex` resume templates using provided data.  
- **`Evaluator Agent`** — reviews `.tex` output and provides improvement feedback.  
- **Gradio Frontend** — upload resumes, provide job URLs, and chat with your assistant.

---

