# utils.py
import logging
import os
import json
import math
from itertools import chain
import multiprocessing
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def empty_folder(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.endswith(('.jpg', '.jpeg', '.png')):
            try:
                os.remove(file_path)
                print(f"File {file_name} cancellato con successo.")
            except Exception as e:
                print(f"Errore durante la cancellazione del file {file_name}: {e}")


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


def merge_unique_sbe_fields_json_arrays(array_json_array):
    unique_json_objects = set()
    merged_array = []

    for json_array in array_json_array:
        for json_object in json_array:
            json_str = json.dumps(json_object, sort_keys=True)
            if json_str not in unique_json_objects:
                unique_json_objects.add(json_str)
                merged_array.append(json_object)

    return merged_array


def get_index_intersected_group(new_repeating_group, array_repeating_groups):
    logging.info(f"new_repeating_group items: {new_repeating_group['items']}")
    new_repeating_group_items_set = set(new_repeating_group["items"])
    for index, repeating_group in enumerate(array_repeating_groups, start=0):
        logging.info(f"repeating_group items: {repeating_group['items']}")
        repeating_group_items_set = set(repeating_group["items"])
        if bool(new_repeating_group_items_set & repeating_group_items_set):
            return index
    return -1


def merge_unique_repeating_groups_json_arrays(array_json_array_repeating_groups):
    logging.info(f"array_json_array_repeating_groups: {array_json_array_repeating_groups}")

    array_distinct_repeating_groups = []
    for array_repeating_groups in array_json_array_repeating_groups:
        for repeating_group in array_repeating_groups:
            logging.info(f"array_distinct_repeating_groups: {array_distinct_repeating_groups}")
            index = get_index_intersected_group(repeating_group, array_distinct_repeating_groups)
            logging.info(f"index: {index}")
            if index == -1:
                array_distinct_repeating_groups.append(repeating_group)
            else:
                array_distinct_repeating_groups[index]["items"] += [id for id in repeating_group["items"] if
                                                                    id not in array_distinct_repeating_groups[index][
                                                                        "items"]]

    logging.info(f"FINAL: {array_distinct_repeating_groups}")
    return array_distinct_repeating_groups


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


def get_number_processes(array):
    return max(min(multiprocessing.cpu_count(), len(array)), 1)


def group_texts_in_array(array_strings, number_elements):
    array_grouped_strings = []

    grouped_strings = [array_strings[i:i + number_elements] for i in range(0, len(array_strings), number_elements)]

    for group in grouped_strings:
        concatenated_string = ''.join(group)
        array_grouped_strings.append(concatenated_string)

    return array_grouped_strings


def split_json_arrays(array_of_json_arrays):
    array_splitted_json_arrays = []
    for json_array in array_of_json_arrays:
        if not isinstance(json_array, list):
            raise ValueError("Each item in the array must be a list.")

        split_index = len(json_array) // 2 + len(json_array) % 2

        first_part = json_array[:split_index]
        second_part = json_array[split_index:]

        array_splitted_json_arrays.append(first_part)
        array_splitted_json_arrays.append(second_part)

    return array_splitted_json_arrays


def merge_json_arrays(json_array_of_arrays):
    return list(chain.from_iterable(json_array_of_arrays))


def compute_optimal_group_size(total_items, max_group_size):
    number_group = math.ceil(total_items / max_group_size)
    minimum_group_size = max_group_size
    for i in range(max_group_size - 1, 0, -1):
        if math.ceil(total_items / i) == number_group:
            minimum_group_size = i
        else:
            break
    return minimum_group_size


def group_json_objects(json_objects, group_size):
    return [json_objects[i:i + group_size] for i in range(0, len(json_objects), group_size)]


def generate_optimal_array_of_json_array(json_array_of_arrays, max_group_size):
    merged_json_objects = merge_json_arrays(json_array_of_arrays)
    optimal_group_size = compute_optimal_group_size(len(merged_json_objects), max_group_size)
    grouped_json_objects = group_json_objects(merged_json_objects, optimal_group_size)
    return grouped_json_objects


def add_ai_engine_id(array_json_array_fields):
    current_ai_engine_id = 1
    updated_array_json_array_fields = []

    for json_array_fields in array_json_array_fields:
        updated_json_array_fields = []

        for field in json_array_fields:
            updated_field = field.copy()
            updated_field['ai_engine_id'] = current_ai_engine_id
            current_ai_engine_id += 1
            updated_json_array_fields.append(updated_field)

        updated_array_json_array_fields.append(updated_json_array_fields)

    return updated_array_json_array_fields


def get_repeating_group_sbe_field(ai_engine_id, array_sbe_fields):
    return next(
        filter(
            lambda sbe_field: sbe_field.get('ai_engine_id') == ai_engine_id,
            array_sbe_fields),
        None
    )