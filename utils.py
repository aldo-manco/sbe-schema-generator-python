import os

ai_model_name = "gpt-4-0125-preview"
openai_api_key = ""

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def save_uploaded_file(directory_path, file):
    create_directory_if_not_exists(directory_path)
    file_path = os.path.join(directory_path, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path


def replace_newlines_with_space(input_string):
    return input_string.replace('\n', ' ')

