# 🤖 Streamlit Chat with OpenAI API

A minimal **chat interface** built with [Streamlit](https://streamlit.io/) and the [OpenAI Python SDK](https://github.com/openai/openai-python).  
It uses the **Responses API** with **streaming** support and includes a **🧹 Clean chat** button to reset the conversation.

---

## ✨ Features
- Simple chat UI powered by Streamlit’s `st.chat_message`.
- Sidebar controls:
  - Select the model (default: `gpt-5-nano`)
  - Adjust verbosity and reasoning effort.
  - **Clean chat** button to reset history.
- Conversation history persisted in `st.session_state`.
- **Streaming responses** (assistant reply updates token by token).
- Works with `OPENAI_API_KEY` stored in:
  - `.streamlit/secrets.toml`  
  - or as an environment variable.

---

## 📦 Installation

Clone this repo and install dependencies:

```bash
git clone https://github.com/MottaDavide/streamlit-openai-chat.git
cd streamlit-openai-chat
```

### 𖠉 Installation with pip

```
# Create virtual environment (optional)
python -m venv .venv
source .venv/bin/activate   # on Linux/Mac
.venv\Scripts\activate      # on Windows

# Install dependencies
pip install -r requirements.txt
```

### 🐍 Installation with Conda

```bash
# Create the environment from the YAML file
conda env create -f environment.yaml

# Activate it
conda activate streamlit-openai-chat
```

## 📉 Diagram
```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant S as Streamlit UI
    participant A as App (Python)
    participant O as OpenAI Responses API

    U->>S: Type message (st.chat_input)
    S->>A: Submit prompt
    A->>A: Build messages[] (history)
    A->>O: responses.stream(model, input=messages, ...)
    activate O

    loop Event stream
        O-->>A: event = response.output_text.delta
        A->>A: full_text += event.delta
        A->>S: placeholder.markdown(full_text)
    end

    O-->>A: [end-of-stream signal]
    deactivate O

    A->>S: Final render (assistant bubble)
    A->>A: Save reply into session_state.messages
```