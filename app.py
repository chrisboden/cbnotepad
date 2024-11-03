import os
import streamlit as st
import google.generativeai as genai
from google.generativeai import types
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import tempfile
import json
import time
from pathlib import Path

# Initialize environment and API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def wait_for_files_active(files, timeout=300, check_interval=10):
    """
    Waits until all provided Gemini files are in the 'ACTIVE' state.
    """
    start_time = time.time()
    for file in files:
        print(f"Checking status of file: {file.name}")
        while True:
            current_file = genai.get_file(name=file.name)
            status = current_file.state.name
            print(f"Current status of '{file.name}': {status}")
            if status == "ACTIVE":
                print(f"File '{file.name}' is ACTIVE.")
                break
            elif status == "FAILED":
                raise Exception(f"File '{file.name}' failed to process.")
            elif time.time() - start_time > timeout:
                raise Exception(f"Timeout while waiting for file '{file.name}' to become ACTIVE.")
            else:
                print(f"Waiting for file '{file.name}' to become ACTIVE...")
                time.sleep(check_interval)
    print("All files are ACTIVE and ready for use.")

def verify_files_active(files):
    """Verify all files are in ACTIVE state before proceeding"""
    for file in files:
        current_file = genai.get_file(name=file.name)
        if current_file.state.name != "ACTIVE":
            return False
    return True

def clear_chat_history():
    st.session_state.messages = []

def user_input(user_question):
    # Debug logging for file access
    selected_files = [file_info["gemini_file"] for file_info in st.session_state.uploaded_files if file_info["selected"]]
    print("\n=== Available Files ===")
    for file in selected_files:
        print(f"File: {file.display_name} | Name: {file.name}")

    # Load prompt configuration
    with open('prompt.json', 'r') as f:
        prompt_config = json.load(f)

    # Create generation config
    generation_config = types.GenerationConfig(
        temperature=prompt_config.get("temperature", 0.7),
        max_output_tokens=prompt_config.get("max_tokens", 8092),
        top_p=0.8,
        top_k=40
    )

    # Initialize model with enhanced system prompt
    model = genai.GenerativeModel(
        model_name=prompt_config.get("model", "gemini-1.5-pro-002"),
        generation_config=generation_config,
        system_instruction=prompt_config["messages"][0]["content"],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    # Convert session messages to chat history
    history = []
    for msg in st.session_state.messages[:-1]:  # Exclude latest user message
        history.append({
            "role": msg["role"],
            "parts": [msg["content"]]
        })

    print("\nConverted Chat History:")
    print(json.dumps(history, indent=2))

    # Start chat with history
    chat = model.start_chat(history=history)

    # Prepare message with explicit file listing
    file_list = "\n".join([f"- {f.display_name}" for f in selected_files])
    enhanced_prompt = f"""
    User question: {user_question}
    \n\n
    IMPORTANT: Note that the user has provided these specific documents 
    for you to analyse and use in your response:
    \n\n
    {file_list}
    \n\n
    Please ensure you use ALL of the available documents for your response."""

    # Send message with files and enhanced prompt
    message_parts = selected_files + [enhanced_prompt]

    print("\nCurrent Message Parts:")
    print(f"- Files: {[f.display_name for f in selected_files]}")
    print(f"- Enhanced Prompt: {enhanced_prompt}")
    print("===============================================\n")

    try:
        response = chat.send_message(message_parts)
        return response
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        print(f"Error details: {str(e)}")
        return None

def main():
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "uploaded_file_names" not in st.session_state:
        st.session_state.uploaded_file_names = set()

    # Sidebar for uploading files
    with st.sidebar:
        uploaded_docs = st.file_uploader(
            "Upload documents for analysis", 
            accept_multiple_files=True
        )

        if uploaded_docs:
            uploaded_gemini_files = []
            with st.spinner("Processing uploads..."):
                for uploaded_file in uploaded_docs:
                    if uploaded_file.name not in st.session_state.uploaded_file_names:
                        mime_type = uploaded_file.type
                        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file.flush()
                            tmp_file_name = tmp_file.name
                        
                        try:
                            gemini_file = genai.upload_file(
                                tmp_file_name,
                                mime_type=mime_type,
                                display_name=uploaded_file.name
                            )
                            uploaded_gemini_files.append(gemini_file)
                            
                            st.session_state.uploaded_files.append({
                                "name": uploaded_file.name,
                                "gemini_file": gemini_file,
                                "selected": True
                            })
                            st.session_state.uploaded_file_names.add(uploaded_file.name)
                        except Exception as e:
                            st.error(f"Failed to upload {uploaded_file.name}: {str(e)}")
                        finally:
                            os.unlink(tmp_file_name)

            # Wait for all uploaded files to become ACTIVE
            if uploaded_gemini_files:
                try:
                    wait_for_files_active(uploaded_gemini_files)
                    st.success("Files uploaded and processed successfully.")
                except Exception as e:
                    st.error(str(e))

        # Display file selection checkboxes
        if st.session_state.uploaded_files:
            st.write("Select files to include in the analysis:")
            for idx, file_info in enumerate(st.session_state.uploaded_files):
                file_info["selected"] = st.checkbox(
                    file_info["name"],
                    value=file_info.get("selected", True),
                    key=f"{file_info['name']}_{idx}"
                )

        st.button('Clear Chat History', on_click=clear_chat_history)

    # Main chat interface

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display response
        if st.session_state.uploaded_files:
            selected_files = [f["gemini_file"] for f in st.session_state.uploaded_files if f["selected"]]
            if not verify_files_active(selected_files):
                st.warning("Some files are still processing. Please wait a moment before asking questions.")
                return
            
            if not selected_files:
                st.warning("Please select at least one file to analyze.")
                return
                
            with st.chat_message("assistant"):
                with st.spinner("Analyzing documents..."):
                    response = user_input(prompt)
                    if response is not None:
                        full_response = response.text
                        st.markdown(full_response)
                        message = {"role": "assistant", "content": full_response}
                        st.session_state.messages.append(message)
        else:
            st.warning("Please upload at least one document before asking questions.")

if __name__ == "__main__":
    main()