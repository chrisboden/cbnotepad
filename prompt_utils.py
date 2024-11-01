import os
import re
import glob
from datetime import datetime

def get_full_path(file_path):
    return os.path.join(os.getcwd(), file_path)

def include_directory_content(match, depth=5, file_delimiter=None):
    if depth <= 0:
        return "[ERROR: Maximum inclusion depth reached]"
    
    dir_pattern = match.group(1).strip()
    full_dir_pattern = get_full_path(dir_pattern)
    
    try:
        matching_files = glob.glob(full_dir_pattern)
        if not matching_files:
            return f"[ERROR: No files found matching {dir_pattern}]"
        
        contents = []
        for file_path in matching_files:
            with open(file_path, 'r') as f:
                content = f.read()
            content = process_inclusions(content, depth - 1, file_delimiter)
            if file_delimiter is not None:
                contents.append(f"{file_delimiter.format(filename=os.path.basename(file_path))}\n{content}")
            else:
                contents.append(content)
        
        return "\n".join(contents)
    except Exception as e:
        return f"[ERROR: Failed to process directory {dir_pattern}: {str(e)}]"

def include_file_content(match, depth=5):
    if depth <= 0:
        return "[ERROR: Maximum inclusion depth reached]"
    
    file_to_include = match.group(1).strip()
    full_file_path = get_full_path(file_to_include)
    try:
        with open(full_file_path, 'r') as f:
            content = f.read()
        return process_inclusions(content, depth - 1)
    except FileNotFoundError:
        return f"[ERROR: File {file_to_include} not found]"

def get_current_datetime(match):
    format_string = match.group(1).strip() if match.group(1) else "%Y-%m-%d %H:%M:%S"
    try:
        return datetime.now().strftime(format_string)
    except Exception as e:
        return f"[ERROR: Invalid datetime format: {format_string}]"

def process_inclusions(content, depth, file_delimiter=None):
    content = re.sub(r'<\$datetime:(.*?)\$>', get_current_datetime, content)
    content = re.sub(r'<\$dir:(.*?)\$>', lambda m: include_directory_content(m, depth, file_delimiter), content)
    content = re.sub(r'<\$(.*?)\$>', lambda m: include_file_content(m, depth), content)
    return content

def load_prompt(advisor_data, conversation_history, max_depth=5, file_delimiter=None):
    conversation_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])

    for message in advisor_data["messages"]:
        if '<$conversation_history$>' in message["content"]:
            message["content"] = message["content"].replace('<$conversation_history$>', conversation_history_str)

        message["content"] = process_inclusions(message["content"], max_depth, file_delimiter)

    return advisor_data["messages"]
