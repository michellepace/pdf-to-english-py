# Deployment Options

## Railway

Railway auto-detects Python projects. The key configuration is binding Gradio to all network interfaces (it defaults to localhost only).

**Required files:**

```
your-project/
├── app.py              # Your Gradio app
├── pyproject.toml      # Dependencies (uv project)
└── Procfile            # Optional but recommended
```

**Procfile:**

```
web: python app.py
```

**Key Configuration — Gradio launch settings:**

```python
import gradio as gr

demo = gr.Interface(...)

demo.launch(
    server_name="0.0.0.0",  # Critical: bind to all interfaces (not localhost)
    server_port=7860,
    share=False
)
```

**Why this matters:** Gradio defaults to `127.0.0.1:7860` (localhost only), which is inaccessible from Railway's network. Setting `server_name="0.0.0.0"` allows external access.

**References:**

- [Railway Support Forum: Running a Gradio app](https://station.railway.com/questions/running-an-app-built-using-gradio-36279073)
- [Deploy Gradio on Railway (Medium, Dec 2025)](https://medium.com/@kumaresankp21/deploy-your-gradio-app-on-railway-for-free-in-2025-complete-step-by-step-guide-0148b1bf73e0)

---

## Hugging Face Spaces

Hugging Face Spaces provides free, zero-configuration hosting for Gradio apps. It's the simplest deployment option for prototypes.

**Setup:**

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select "Gradio" as the SDK
3. Push your code (or connect to GitHub)

**Required files:**

```
your-project/
├── app.py              # Your Gradio app (entry point)
└── requirements.txt    # Dependencies
```

**Key Configuration — No special launch settings needed:**

```python
import gradio as gr

demo = gr.Interface(...)

demo.launch()  # HF Spaces handles host/port automatically
```

**Environment variables:** Set `MISTRAL_API_KEY` in Space Settings → Variables and Secrets.

**References:**

- [Gradio Quickstart: Sharing Your Demo](https://www.gradio.app/guides/quickstart#sharing-your-demo)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
