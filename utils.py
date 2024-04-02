import os
import shutil
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate
)


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def empty_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def save_uploaded_file(directory_path, file):
    create_directory_if_not_exists(directory_path)
    file_path = os.path.join(directory_path, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path


def is_duplicate_in_json_array(field_name, field_value, json_array_fields):
    try:
        for item in json_array_fields:
            if item.get(field_name) == field_value:
                return True
        return False
    except json.JSONDecodeError:
        raise ValueError("Il terzo argomento deve essere un JSON array.")
    except TypeError:
        raise ValueError("Il campo fornito non esiste o il valore non è confrontabile.")


def merge_unique_json_arrays(array_json_array):
    unique_json_objects = set()
    merged_array = []

    for json_array in array_json_array:
        for json_object in json_array:
            json_str = json.dumps(json_object, sort_keys=True)
            if json_str not in unique_json_objects:
                unique_json_objects.add(json_str)
                merged_array.append(json_object)

    return merged_array


def replace_newlines_with_space(input_string):
    return input_string.replace('\n', ' ')


def clean_json_string(json_string):
    cleaned_str = json_string.strip()
    cleaned_str = cleaned_str.replace("```json\n", "", 1)
    cleaned_str = cleaned_str.rsplit("\n```", 1)[0]

    return cleaned_str


def escape_braces_for_formatting(input_string):
    return (input_string
            .replace('{', '{{')
            .replace('}', '}}'))


def get_env_variables():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_ai_model_name = os.getenv("OPENAI_AI_MODEL_NAME")

    return openai_api_key, openai_ai_model_name


def get_output_from_generative_ai(
        system_message,
        example_1_human_message,
        example_1_assistant_message,
        example_2_human_message,
        example_2_assistant_message,
        example_3_human_message,
        example_3_assistant_message,
        example_4_human_message,
        example_4_assistant_message,
        human_message
):
    openai_api_key, openai_ai_model_name = get_env_variables()

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=openai_ai_model_name,
        temperature=0.0
    )

    array_examples = []
    add_example_in_array(
        array_examples,
        example_1_human_message,
        example_1_assistant_message
    )
    add_example_in_array(
        array_examples,
        example_2_human_message,
        example_2_assistant_message
    )
    add_example_in_array(
        array_examples,
        example_3_human_message,
        example_3_assistant_message
    )
    add_example_in_array(
        array_examples,
        example_4_human_message,
        example_4_assistant_message
    )

    prompt = [
        SystemMessage(content=system_message)
    ]

    for example in array_examples:
        prompt.append(HumanMessage(content=example["human_message"]))
        prompt.append(AIMessage(content=example["ai_message"]))

    prompt.append(HumanMessage(content=human_message))

    output_parser = StrOutputParser()

    chain = llm | output_parser

    return clean_json_string(chain.invoke(prompt))


def add_example_in_array(array_examples, example_human_message, example_assistant_message):
    if example_human_message != "" and example_assistant_message != "":
        array_examples.append({
            "human_message": example_human_message,
            "ai_message": example_assistant_message,
        })