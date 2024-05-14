# ai_utils.py

import os
import json
import logging
import pickle
from pathlib import Path
import re

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from prompts import generate_repeating_groups_prompt
from prompts import generate_document_fields_prompt
from prompts import generate_sbe_fields_prompt

from prompts import generate_datatype_from_embeddings_prompt
from prompts import generate_presence_from_embeddings_prompt
from prompts import generate_char_attributes_from_embeddings_prompt
from prompts import generate_enumerations_set_attributes_from_embeddings_prompt

from utils import utils


def clean_json_string(
        json_string
):
    cleaned_str = json_string.strip()
    cleaned_str = cleaned_str.replace("```json\n", "", 1)
    cleaned_str = cleaned_str.rsplit("\n```", 1)[0]

    return cleaned_str


def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")


def get_powerful_ai_model_name():
    return os.getenv("POWERFUL_AI_MODEL_NAME")


def get_economic_ai_model_name():
    return os.getenv("ECONOMIC_AI_MODEL_NAME")


def get_openai_ai_embeddings_model_name():
    return os.getenv("AI_EMBEDDINGS_MODEL")


def get_output_from_generative_ai(
        ai_model_name,
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
    openai_api_key = get_openai_api_key()

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=ai_model_name,
        temperature=0.0,
        model_kwargs={
            "response_format": {"type": "json_object"}
        }
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


def add_example_in_array(
        array_examples,
        example_human_message,
        example_assistant_message
):
    if example_human_message != "" and example_assistant_message != "":
        array_examples.append({
            "human_message": example_human_message,
            "ai_message": example_assistant_message,
        })


def generate_document_fields(
        array_text_pages
):
    ai_model_name = get_economic_ai_model_name()

    human_message = f"""
### INPUT ###

{array_text_pages}

### OUTPUT JSON ###
        """

    output = get_output_from_generative_ai(
        ai_model_name,
        generate_document_fields_prompt.system_message,
        generate_document_fields_prompt.example_1_human_message,
        generate_document_fields_prompt.example_1_assistant_message,
        generate_document_fields_prompt.example_2_human_message,
        generate_document_fields_prompt.example_2_assistant_message,
        generate_document_fields_prompt.example_3_human_message,
        generate_document_fields_prompt.example_3_assistant_message,
        generate_document_fields_prompt.example_4_human_message,
        generate_document_fields_prompt.example_4_assistant_message,
        human_message
    )

    logging.info(f"\n\nDOCUMENT FIELDS: {output}\n\n")

    return json.loads(output)['json_array']


def generate_repeating_groups(
        array_document_fields
):
    ai_model_name = get_powerful_ai_model_name()

    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
    """

    output = get_output_from_generative_ai(
        ai_model_name,
        generate_repeating_groups_prompt.system_message,
        generate_repeating_groups_prompt.example_1_human_message,
        generate_repeating_groups_prompt.example_1_assistant_message,
        generate_repeating_groups_prompt.example_2_human_message,
        generate_repeating_groups_prompt.example_2_assistant_message,
        generate_repeating_groups_prompt.example_3_human_message,
        generate_repeating_groups_prompt.example_3_assistant_message,
        generate_repeating_groups_prompt.example_4_human_message,
        generate_repeating_groups_prompt.example_4_assistant_message,
        human_message
    )

    logging.info(f"\n\nREPEATING GROUPS: {output}\n\n")

    return json.loads(output)['json_array']


def generate_basic_sbe_fields(
        array_document_fields
):
    ai_model_name = get_economic_ai_model_name()

    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
        """

    output = get_output_from_generative_ai(
        ai_model_name,
        generate_sbe_fields_prompt.system_message,
        generate_sbe_fields_prompt.example_1_human_message,
        generate_sbe_fields_prompt.example_1_assistant_message,
        generate_sbe_fields_prompt.example_2_human_message,
        generate_sbe_fields_prompt.example_2_assistant_message,
        generate_sbe_fields_prompt.example_3_human_message,
        generate_sbe_fields_prompt.example_3_assistant_message,
        generate_sbe_fields_prompt.example_4_human_message,
        generate_sbe_fields_prompt.example_4_assistant_message,
        human_message
    )

    logging.info(f"\n\nSBE FIELDS: {output}\n\n")

    return json.loads(output)['json_array']


def generate_unknown_attributes_from_embeddings(
        ai_engine_id,
        document_field,
        array_embeddings,
        prompt_handler,
        log_name,
):
    ai_model_name = get_economic_ai_model_name()

    string_array_document_fields = json.dumps(document_field)
    string_array_embeddings = json.dumps(array_embeddings)

    human_message = f"""
### INPUT: SBE FIELD DESCRIPTION ###

{string_array_document_fields}

{string_array_embeddings}

### OUTPUT JSON ###
            """

    output = get_output_from_generative_ai(
        ai_model_name,
        prompt_handler.system_message,
        prompt_handler.example_1_human_message,
        prompt_handler.example_1_assistant_message,
        prompt_handler.example_2_human_message,
        prompt_handler.example_2_assistant_message,
        prompt_handler.example_3_human_message,
        prompt_handler.example_3_assistant_message,
        prompt_handler.example_4_human_message,
        prompt_handler.example_4_assistant_message,
        human_message
    )

    logging.info(f"\n\n{log_name}: {output}\n\n")

    return {
        ai_engine_id: json.loads(output)
    }


def get_array_pdf_partitions(
        array_pdf_pages_texts,
        chunk_size,
        chunk_overlap
):
    pdf_content = "".join(array_pdf_pages_texts)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    return text_splitter.split_text(text=pdf_content)


def get_embeddings_file_path(
        pdf_path
):
    embeddings_root_folder_name = "embeddings"
    utils.create_directory_if_not_exists(embeddings_root_folder_name)
    embeddings_file_name = utils.extract_pdf_filename(pdf_path)
    embeddings_folder_name = f"{embeddings_file_name}"
    utils.create_directory_if_not_exists(embeddings_folder_name)
    embeddings_file_path = Path(embeddings_root_folder_name, embeddings_folder_name)
    return embeddings_file_path, embeddings_file_name


def create_storage_embeddings(
        pdf_path,
        array_pdf_pages_texts,
        chunk_size: int,
        chunk_overlap: int
):
    array_pdf_partitions = get_array_pdf_partitions(
        array_pdf_pages_texts,
        chunk_size,
        chunk_overlap
    )

    openai_api_key = get_openai_api_key()
    openai_ai_embeddings_model_name = get_openai_ai_embeddings_model_name()

    embeddings_ai_model = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        model=openai_ai_embeddings_model_name
    )

    embeddings_file_path, embeddings_file_name = get_embeddings_file_path(pdf_path)

    storage_embeddings = get_existing_storage_embeddings(
        embeddings_file_path,
        embeddings_file_name
    )

    if storage_embeddings is None:
        storage_embeddings = FAISS.from_texts(
            array_pdf_partitions,
            embedding=embeddings_ai_model
        )
        storage_embeddings.save_local(
            folder_path=embeddings_file_path,
            index_name=embeddings_file_name
        )


def get_existing_storage_embeddings(
        embeddings_file_path,
        embeddings_file_name
):
    openai_api_key = get_openai_api_key()
    openai_ai_embeddings_model_name = get_openai_ai_embeddings_model_name()

    embeddings_ai_model = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        model=openai_ai_embeddings_model_name
    )

    try:
        return FAISS.load_local(
            folder_path=embeddings_file_path,
            embeddings=embeddings_ai_model,
            index_name=embeddings_file_name,
            allow_dangerous_deserialization=True
        )
    except:
        return None


def indepth_document_fields(
        array_json_array_document_fields,
        pdf_path
):
    embeddings_file_path, embeddings_file_name = get_embeddings_file_path(pdf_path)
    pdf_storage_embeddings = get_existing_storage_embeddings(
        embeddings_file_path,
        embeddings_file_name
    )

    number_related_chunks = 1
    for json_array_document_fields in array_json_array_document_fields:
        for document_field in json_array_document_fields:
            document_field_query = "The possible values of the following field -> "
            document_field_query += utils.dictionary_to_string(document_field)

            document_field['relevant_information'] = get_related_information(
                pdf_storage_embeddings,
                document_field_query,
                number_related_chunks
            )


def get_related_information(
        storage_embeddings,
        document_field_query,
        number_related_chunks
):
    related_chunks = storage_embeddings.similarity_search(
        query=document_field_query,
        k=number_related_chunks
    )

    i = 1
    related_chunks_text = ""
    for related_chunk in related_chunks:
        related_chunks_text += f" ### INPUT: CONTEXT {i} ### "
        related_chunks_text += related_chunk.page_content
        i = i + 1

    return related_chunks_text


def fill_dictionary_with_document_fields(
        ai_engine_id_to_empty,
        array_document_fields
):
    for ai_engine_id in ai_engine_id_to_empty.keys():
        for document_field in array_document_fields:
            if document_field['ai_engine_id'] == ai_engine_id:
                ai_engine_id_to_empty[ai_engine_id] = document_field
                break


def get_unknown_attributes_from_embeddings(
        ai_engine_id_to_document_field,
        unknown_attributes_prompt_handler,
        pdf_storage_embeddings,
        document_field_query,
        log_name
):
    number_related_chunks = 5

    for ai_engine_id, document_field in ai_engine_id_to_document_field.items():
        document_field_query += utils.dictionary_to_string(document_field)

        array_embeddings = get_related_information(
            pdf_storage_embeddings,
            document_field_query,
            number_related_chunks
        )

        ai_engine_id_to_document_field[ai_engine_id] = generate_unknown_attributes_from_embeddings(
            ai_engine_id,
            document_field,
            array_embeddings,
            unknown_attributes_prompt_handler,
            log_name
        )


def extend_array_sbe_fields(
        ai_engine_id_to_new_attributes,
        array_sbe_fields
):
    for sbe_field in array_sbe_fields:
        for ai_engine_id, dictionary_new_attributes in ai_engine_id_to_new_attributes.items():
            if sbe_field.get('ai_engine_id') == ai_engine_id:
                for name_attribute, value_attribute in dictionary_new_attributes.items():
                    sbe_field[name_attribute] = value_attribute
                break


def update_array_sbe_fields_with_unknown_attributes(
        dictionary_new_attributes,
        unknown_attributes_prompt_handler,
        array_sbe_fields,
        array_document_fields,
        pdf_storage_embeddings,
        document_field_query,
        log_name
):
    fill_dictionary_with_document_fields(
        dictionary_new_attributes,
        array_document_fields
    )

    get_unknown_attributes_from_embeddings(
        dictionary_new_attributes,
        unknown_attributes_prompt_handler,
        pdf_storage_embeddings,
        document_field_query,
        log_name
    )

    extend_array_sbe_fields(
        dictionary_new_attributes,
        array_sbe_fields
    )


def generate_completed_sbe_fields(
        tuple_array_document_sbe_fields,
        pdf_path
):
    embeddings_file_path, embeddings_file_name = get_embeddings_file_path(
        pdf_path
    )
    pdf_storage_embeddings = get_existing_storage_embeddings(
        embeddings_file_path,
        embeddings_file_name
    )

    unknown_datatype_sbe_fields = {}
    unknown_presence_sbe_fields = {}
    array_numeric_datatypes = ['int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
    array_alphanumeric_datatypes = ['char']
    array_valid_datatypes = array_numeric_datatypes + array_alphanumeric_datatypes
    array_valid_presences = ["mandatory", "optional"]

    array_document_fields, array_sbe_fields = tuple_array_document_sbe_fields
    for document_field, sbe_field in zip(array_document_fields, array_sbe_fields):
        ai_engine_id = sbe_field['ai_engine_id']

        if ('data_type' not in sbe_field
                or sbe_field['data_type'] not in array_valid_datatypes
                or re.search(r'\b(enum|set)$', sbe_field['data_type'])
        ):
            unknown_datatype_sbe_fields[ai_engine_id] = {}

        if ('presence' not in sbe_field
                or sbe_field['presence'] not in array_valid_presences
        ):
            unknown_presence_sbe_fields[ai_engine_id] = {}

    update_array_sbe_fields_with_unknown_attributes(
        unknown_datatype_sbe_fields,
        generate_datatype_from_embeddings_prompt,
        array_sbe_fields,
        array_document_fields,
        pdf_storage_embeddings,
        "The primitive datatype of the following field -> ",
        "DATATYPE"
    )

    update_array_sbe_fields_with_unknown_attributes(
        unknown_presence_sbe_fields,
        generate_presence_from_embeddings_prompt,
        array_sbe_fields,
        array_document_fields,
        pdf_storage_embeddings,
        "The presence (mandatory/optional) of the following field -> ",
        "PRESENCE"
    )

    unknown_char_attributes_sbe_fields = {}
    unknown_enumerations_set_attributes_sbe_fields = {}

    for sbe_field in array_sbe_fields:
        ai_engine_id = sbe_field['ai_engine_id']
        assert 'data_type' in sbe_field, "\'data_type\' must exist"

        if sbe_field['data_type'] in array_numeric_datatypes:
            continue
        elif sbe_field['data_type'] in array_alphanumeric_datatypes:
            if 'length' not in sbe_field:
                unknown_char_attributes_sbe_fields[ai_engine_id] = {}
        elif re.search(r'\b(enum|set)$', sbe_field['data_type']):
            logging.info("ENUMENUMENUM")
            if 'possible_values' not in sbe_field or not sbe_field['possible_values']:
                unknown_enumerations_set_attributes_sbe_fields[ai_engine_id] = {}

    update_array_sbe_fields_with_unknown_attributes(
        unknown_char_attributes_sbe_fields,
        generate_char_attributes_from_embeddings_prompt,
        array_sbe_fields,
        array_document_fields,
        pdf_storage_embeddings,
        "The length in byte of the following alphanumeric field -> ",
        "CHAR ATTRIBUTES"
    )

    update_array_sbe_fields_with_unknown_attributes(
        unknown_enumerations_set_attributes_sbe_fields,
        generate_enumerations_set_attributes_from_embeddings_prompt,
        array_sbe_fields,
        array_document_fields,
        pdf_storage_embeddings,
        "The possible values and the encoding type of the following enumeration/set field -> ",
        "ENUMERATIONS SET ATTRIBUTES"
    )
