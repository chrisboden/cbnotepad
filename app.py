import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile
import json
from prompt_utils import load_prompt
from google.generativeai import types  # Import GenerationConfig

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def clear_chat_history():
    st.session_state.messages = []


def user_input(user_question):
    # Get selected files
    selected_files = [file_info["gemini_file"] for file_info in st.session_state.uploaded_files if file_info["selected"]]
    print("\n=== Selected Files ===")
    print(f"Number of files selected: {len(selected_files)}")
    for file in selected_files:
        print(f"File: {file.display_name}")

    # Load prompt configuration
    with open('prompt.json', 'r') as f:
        prompt_config = json.load(f)

    # Get model parameters
    model_name = prompt_config.get("model", "gemini-1.5-flash-8b")
    temperature = prompt_config.get("temperature", 0.7)
    max_tokens = prompt_config.get("max_tokens", 8092)

    print("\n=== Model Configuration ===")
    print(f"Model: {model_name}")
    print(f"Temperature: {temperature}")
    print(f"Max tokens: {max_tokens}")

    # Create generation config
    generation_config = types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    # Instantiate the model
    model = genai.GenerativeModel(model_name=model_name)

    # Prepare the current message parts (files + question)
    current_parts = selected_files + [user_question]
    print("\n=== Current Message Parts ===")
    print("Parts structure:")
    for i, part in enumerate(current_parts):
        if hasattr(part, 'display_name'):  # If it's a file
            print(f"Part {i}: File - {part.display_name}")
        else:  # If it's the question
            print(f"Part {i}: Text - {part}")

    # Convert existing conversation history to Gemini's format
    history = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            history.append({
                "role": "user",
                "parts": [msg["content"]]
            })
        elif msg["role"] == "assistant":
            history.append({
                "role": "model",
                "parts": [msg["content"]]
            })

    print("\n=== Conversation History Format ===")
    print(json.dumps(history, indent=2, default=str))

    print("\n=== Current Message Format ===")
    current_message = {
        "role": "user",
        "parts": current_parts
    }
    print(json.dumps(current_message, indent=2, default=str))

    # Start chat with history
    chat = model.start_chat(history=history)

    # Send message with files and question
    response = chat.send_message(
        current_parts,
        generation_config=generation_config
    )

    print("\n=== Response Received ===")
    print(f"Response text length: {len(response.text)}")

    return response


def main():
    st.set_page_config(
        page_title="Gemini File Chatbot",
        page_icon="🤖"
    )

    # Initialize session state variables
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
        st.session_state.uploaded_file_names = set()

        # Fetch existing files from Gemini
        with st.spinner("Fetching uploaded files from Gemini..."):
            gemini_files = genai.list_files()
            for gemini_file in gemini_files:
                if gemini_file.display_name not in st.session_state.uploaded_file_names:
                    st.session_state.uploaded_files.append({
                        "name": gemini_file.display_name,
                        "gemini_file": gemini_file,
                        "selected": True
                    })
                    st.session_state.uploaded_file_names.add(gemini_file.display_name)
            st.success("Fetched uploaded files.")

    if 'prev_uploaded_file_names' not in st.session_state:
        st.session_state.prev_uploaded_file_names = set()

    # Sidebar for uploading files
    with st.sidebar:
        #st.title("Menu:")
        uploaded_docs = st.file_uploader(
            "Drag and drop files here", accept_multiple_files=True)

        if uploaded_docs:
            current_uploaded_file_names = set(file.name for file in uploaded_docs)
            new_file_names = current_uploaded_file_names - st.session_state.prev_uploaded_file_names
            if new_file_names:
                new_files = [file for file in uploaded_docs if file.name in new_file_names]
                with st.spinner("Uploading..."):
                    for uploaded_file in new_files:
                        if uploaded_file.name not in st.session_state.uploaded_file_names:
                            mime_type = uploaded_file.type
                            # Create a temporary file
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_file.flush()
                                tmp_file_name = tmp_file.name
                            # Upload to Gemini
                            gemini_file = genai.upload_file(tmp_file_name, mime_type=mime_type, display_name=uploaded_file.name)
                            # Store the gemini_file (which is a File object)
                            st.session_state.uploaded_files.append({"name": uploaded_file.name, "gemini_file": gemini_file, "selected": True})
                            # Keep track of uploaded file names
                            st.session_state.uploaded_file_names.add(uploaded_file.name)
                            # Delete the temporary file
                            os.unlink(tmp_file_name)
                        else:
                            st.warning(f"File '{uploaded_file.name}' has already been uploaded.")
                st.success("Files Uploaded")
            # Update the previous uploaded file names
            st.session_state.prev_uploaded_file_names = current_uploaded_file_names
        else:
            st.session_state.prev_uploaded_file_names = set()

        # Now display the list of uploaded files with checkboxes
        if st.session_state.uploaded_files:
            st.write("Select files to include in the prompt:")
            for idx, file_info in enumerate(st.session_state.uploaded_files):
                file_info["selected"] = st.checkbox(file_info["name"], value=file_info.get("selected", True), key=file_info["name"]+str(idx))
        st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

    # Main content area for displaying chat messages
    #st.title("Chat with files using Gemini 🤖")
    st.write("Welcome to the chat!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Display chat messages and bot response
        if st.session_state.uploaded_files:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = user_input(prompt)
                    full_response = response.text
                    st.write(full_response)
            if response is not None:
                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)
        else:
            st.warning("Please upload and select at least one file before asking a question.")

if __name__ == "__main__":
    main()
