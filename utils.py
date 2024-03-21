import os

ai_model_name = "gpt-4-0125-preview"
openai_api_key = ""

def create_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

