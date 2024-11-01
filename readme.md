# CBNotepad

A Streamlit application that allows users to upload files, include them in prompts, and interact with the Google Gemini API to chat with their documents. The app supports placeholder processing in prompts and maintains uploaded files across sessions. It makes use of Gemini's 1m token context windows and its ability to work with complex file types, natively, without having to parse them to text.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Getting a Google Gemini API Key](#getting-a-google-gemini-api-key)
- [Setting Up the Environment Variables](#setting-up-the-environment-variables)
- [Running the App](#running-the-app)
- [Usage](#usage)
- [Files in the Repository](#files-in-the-repository)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **File Upload and Management**: Upload multiple files (e.g., PDFs) and manage them with checkboxes to include or exclude them from prompts.
- **Persistent File Storage**: Uploaded files are stored and fetched from the Google Gemini API, persisting across sessions.
- **Customizable Prompts**: Use an external JSON file (`prompt_notebooklm.json`) to specify the model, temperature, max tokens, and prompt messages.
- **Placeholder Processing**: Support for placeholders in prompts, such as including file contents and current datetime.
- **Interactive Chat Interface**: A user-friendly chat interface built with Streamlit, maintaining conversation history.

## Prerequisites

- Python 3.7 or higher
- [Pipenv](https://pipenv.pypa.io/en/latest/) or `pip` for dependency management
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/chrisboden/geminotes.git
   cd geminotes
   ```

2. **Create a Virtual Environment and Install Dependencies**

   You can use `pip` for dependency management.


     ```bash
     pip install -r requirements.txt
     ```

## Getting a Google Gemini API Key

1. **Sign Up for Google Cloud Platform (GCP)**

   If you don't already have a GCP account, sign up at [https://cloud.google.com/](https://cloud.google.com/).

2. **Enable the Google Gemini API**

   - Navigate to the Google Cloud Console.
   - Select or create a new project.
   - Enable the Google Gemini API for your project.

3. **Obtain an API Key**

   - Get your api key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Setting Up the Environment Variables

1. **Open the `.env` File**

   Open the `.env` file in the root directory of the project.

2. **Add Your API Key**

   Replace `YOUR_GOOGLE_API_KEY` with your actual Google Gemini API key.

   ```env
   GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
   ```

## Running the App

Run the Streamlit app using the following command:

```bash
streamlit run app.py
```

This will start the app on `http://localhost:8501/`. Open this URL in your web browser to access the app.

## Usage

1. **Uploading Files**

   - In the sidebar, drag and drop your files into the file uploader.
   - The files will be uploaded to the Google Gemini API immediately.
   - Previously uploaded files are fetched and displayed when the app loads.

2. **Selecting Files**

   - After uploading, select the files you want to include in the prompt using the checkboxes.
   - By default, all newly uploaded files are selected.

3. **Interacting with the Chatbot**

   - Type your question into the chat input at the bottom of the main content area.
   - The assistant will respond based on the content of the selected files and the prompt configuration.

4. **Clearing Chat History**

   - Use the **Clear Chat History** button in the sidebar to reset the conversation.

## Files in the Repository

- **`app.py`**: The main Streamlit application script.
- **`prompt.json`**: A JSON file containing the prompt configuration, model settings, and messages.
- **`prompt_utils.py`**: A utility module for processing placeholders in the prompt, such as file inclusions and datetime.
- **`.env_copy`**: A template for the environment variables file. Rename to `.env` and add your gemini api key
- **`requirements.txt`**: A list of Python dependencies required to run the app.
- **`README.md`**: Documentation and instructions for the app.
- **`me/example_aboutme.md`**: An example file that can be included in prompts using placeholders.

## Customization

### Modifying the Prompt Configuration

You can do your prompt engineering in the system instructions in the prompt.json file. It includes the ability to 'include' or pull in content from other files to build out your prompt, eg custom instructions, about me, etc
- **Edit `prompt.json`** to adjust the model parameters and system prompts.
- **Placeholders**:
  - Include files in the prompt using `<$path/to/file$>`.
  - Insert the current datetime using `<$datetime:%Y-%m-%d$>`.

### Adding Files for Placeholder Inclusion

- Place files you want to include via placeholders in the appropriate directories.
- Ensure the file paths in the placeholders are correct relative to the project's root directory.

### Adjusting Model Parameters

- **Model Name**: You can change the `"model"` field in `prompt.json` to use a different Gemini model.
- **Temperature**: Optional: djust the `"temperature"` field to control the randomness of the model's output.
- **Max Tokens**: Optional: et the `"max_tokens"` field to control the maximum length of the generated response.

## Troubleshooting

- **API Key Errors**: Ensure your Google Gemini API key is correctly set in the `.env` file.
- **File Upload Issues**: Verify that your files are supported by the Google Gemini API and are within size limits.
- **Placeholder Errors**: Check that file paths in placeholders are correct and that files exist.
- **Module Not Found**: Install all dependencies using `pip install -r requirements.txt`.
- **App Crashes or Exceptions**: Review the error messages in the console for details and ensure all configurations are correct.

## License

[MIT License](LICENSE)
