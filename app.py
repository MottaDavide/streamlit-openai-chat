"""
Streamlit App: Minimal chat interface using OpenAI Responses API, with streaming and a "Clean chat" button.

Features:
- Sidebar with model selection and temperature control.
- API key management from Streamlit secrets or environment variable.
- Conversation history persisted in session_state.
- Streaming of assistant responses (progressive rendering).
- "🧹 Clean chat" button to reset the conversation.

Requirements:
- streamlit
- openai (official SDK)
- A valid API key in .streamlit/secrets.toml or as OPENAI_API_KEY environment variable.

Run:
    streamlit run app.py
"""

# --- Standard library ---
import os  # For environment variables

# --- Typing ---
from typing import List, Dict  # For type annotations

# --- Third-party libraries ---
import streamlit as st  # Web UI framework
from openai import OpenAI  # Official OpenAI client


# ---------------------------
# Page config
# ---------------------------
st.set_page_config(
    page_title="Chat with OpenAI",  # Browser tab title
    page_icon="🤖",                 # Emoji/icon for the page
    layout="centered",              # Page layout
)


# ---------------------------
# Helper functions
# ---------------------------
def get_client() -> OpenAI:
    """
    Create and return an authenticated OpenAI client.

    Logic:
    1) First, try to read API key from st.secrets["OPENAI_API_KEY"].
    2) Fallback: check the OPENAI_API_KEY environment variable.
    3) If no key found, show an error in Streamlit and stop execution.

    Returns:
        OpenAI: an authenticated client instance.
    """
    api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ Missing API key. Set OPENAI_API_KEY in .streamlit/secrets.toml or as an env var.")
        st.stop()
    return OpenAI(api_key=api_key)


def init_state() -> None:
    """
    Initialize Streamlit session_state variables if missing.

    Adds:
    - messages: chat history (list of dicts with {role, content})
    - model: default OpenAI model
    - temperature: creativity of the model (0.0–1.0)

    Returns:
        None
    """
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []
    if "model" not in st.session_state:
        st.session_state.model = "gpt-5-nano"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.5


def render_sidebar() -> None:
    """
    Render the sidebar for model/temperature parameters and clean-chat button.

    Includes:
    - Selectbox for choosing the model.
    - Slider for temperature.
    - "🧹 Clean chat" button to reset history.

    Returns:
        None
    """
    st.sidebar.title("⚙️ Parameters")
    st.sidebar.divider()

    # Model selection
    st.session_state.model = st.sidebar.selectbox(
        "Model",
        options=["gpt-5-nano", "gpt-5-mini", "gpt-5"],
        index=0,
    )

    # Verbosity selection
    # This lets you hint the model to be more or less expansive in its replies
    st.session_state.verbosity = st.sidebar.selectbox(
        "Verbosity",
        options=['low','medium','high'],
    )
    
    st.session_state.reasoning_effort = st.sidebar.selectbox(
        "Reasoning effort",
        options=['minimal', 'low','medium','high'],
    )
    


    # Clean chat button
    if st.sidebar.button("🧹 Clean chat", use_container_width=True):
        st.session_state.messages = []  # Reset history
        st.rerun()  # Reload app


def render_history() -> None:
    """
    Display the saved chat history (user + assistant).

    Returns:
        None
    """
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def append_and_render_user(prompt: str) -> None:
    """
    Append user message to chat history and display it immediately.

    Args:
        prompt (str): the message entered by the user

    Returns:
        None
    """
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


def stream_response(
    client: OpenAI, messages: List[Dict[str, str]], model: str, verbosity: str, reasoning_effort: str
) -> str:
    """
    Stream assistant response from the OpenAI Responses API.

    Args:
        client (OpenAI): authenticated client
        messages (List[Dict[str, str]]): full chat history as role/content dicts
        model (str): model name to use
        verbosity (str): verbosity level for the response [low, medium, high]
        reasoning_effort (str): reasoning effort level [minimal, low, medium, high]

    Returns:
        str: the final concatenated assistant message
    """
    full_text = "" # Initialize an empty string to accumulate the assistant’s output as it streams in.
    with st.chat_message("assistant"): # Everything inside this block will be displayed as if the assistant wrote it.
        placeholder = st.empty()  # Placeholder for progressive rendering
        try:
            with client.responses.stream( # Open a streaming connection to the OpenAI Responses API.
                model=model,
                input=messages,
                text={"verbosity": verbosity},
                reasoning={"effort": reasoning_effort},
            ) as stream:
                for event in stream: # Iterate over all events coming from the stream. Each event represents a small chunk of information (e.g. a token, metadata, or final signal).
                    if event.type == "response.output_text.delta": # Check if the event is a text delta, i.e. a new fragment of the assistant’s output.
                        full_text += event.delta
                        placeholder.markdown(full_text) # This makes the assistant’s response appear on the screen token by token (progressive rendering).
                stream.until_done()  # Wait until the stream has fully finished sending all events.
        except Exception as e:
            st.error(f"❌ Error while generating: {e}")
            return ""
    return full_text


# ---------------------------
# Main app
# ---------------------------
init_state()
client = get_client()

st.title("🤖 Chat with OpenAI API")
st.subheader("A simple chat interface using the Responses API (streaming)")

render_sidebar()
st.divider()

# Show history
render_history()

# User input
prompt = st.chat_input("Type your message…")

if prompt:
    append_and_render_user(prompt)

    # Prepare input for the model (whole conversation for context)
    input_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Generate and stream response
    output_text = stream_response(
        client=client,
        messages=input_messages,
        model=st.session_state.model,
        verbosity=st.session_state.verbosity,
        reasoning_effort=st.session_state.reasoning_effort
    )

    # Save assistant reply
    if output_text:
        st.session_state.messages.append({"role": "assistant", "content": output_text})