# ai_utils.py

import os
import json
import logging
import pickle
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from business_logic.prompts import generate_repeating_groups_prompt
from business_logic.prompts import generate_document_fields_prompt
from business_logic.prompts import generate_sbe_fields_prompt

import utils


def clean_json_string(json_string):
    cleaned_str = json_string.strip()
    cleaned_str = cleaned_str.replace("```json\n", "", 1)
    cleaned_str = cleaned_str.rsplit("\n```", 1)[0]

    return cleaned_str


def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")


def get_openai_ai_model_name():
    return os.getenv("OPENAI_AI_MODEL_NAME")


def get_openai_ai_embeddings_model_name():
    return os.getenv("OPENAI_AI_EMBEDDINGS_MODEL")


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
    openai_api_key = get_openai_api_key()
    openai_ai_model_name = get_openai_ai_model_name()

    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=openai_ai_model_name,
        temperature=0.0,
        model_kwargs={"response_format": {"type": "json_object"}}
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


def generate_document_fields(array_text_pages):
    human_message = f"""
### INPUT ###

{array_text_pages}

### OUTPUT JSON ###
        """

    output = get_output_from_generative_ai(
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

    return json.loads(output)


def generate_repeating_groups(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
    """

    output = get_output_from_generative_ai(
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

    return json.loads(output)


def generate_sbe_fields(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
        """

    output = get_output_from_generative_ai(
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

    return json.loads(output)


def generate_embeddings(pdf_file, extracted_information_from_report):
    report_chunk_size = 500
    report_chunk_overlap = 100

    storage_embeddings_report_info = get_storage_embeddings(
        pdf_file=pdf_file,
        pdf_text=extracted_information_from_report,
        chunk_size=report_chunk_size,
        chunk_overlap=report_chunk_overlap
    )


def get_array_pdf_partitions(array_pdf_pages_texts, chunk_size, chunk_overlap):
    pdf_content = "".join(array_pdf_pages_texts)

    # create a text splitter able to create overlapped chunks of a long text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    # partition the string which contains the entire pdf in overlapped chunks
    return text_splitter.split_text(text=pdf_content)


def get_embeddings_file_path(pdf_path):
    embeddings_folder_path = "embeddings"
    utils.create_directory_if_not_exists(embeddings_folder_path)
    pdf_filename = utils.extract_pdf_filename(pdf_path)
    embeddings_file_name = f"embeddings_{pdf_filename}.pkl"
    embeddings_file_path = Path(embeddings_folder_path, embeddings_file_name)
    return embeddings_file_path


def create_storage_embeddings(pdf_path, array_pdf_pages_texts, chunk_size: int, chunk_overlap: int):
    array_pdf_partitions = get_array_pdf_partitions(array_pdf_pages_texts, chunk_size, chunk_overlap)

    openai_api_key = get_openai_api_key()
    openai_ai_embeddings_model_name = get_openai_ai_embeddings_model_name()

    embeddings_ai_model = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        model=openai_ai_embeddings_model_name
    )

    embeddings_file_path = get_embeddings_file_path(pdf_path)

    storage_embeddings = get_existing_storage_embeddings(embeddings_file_path)

    if storage_embeddings is None:
        storage_embeddings = FAISS.from_texts(array_pdf_partitions, embedding=embeddings_ai_model)

        with open(embeddings_file_path, "wb") as f:
            pickle.dump(storage_embeddings, f)


def get_existing_storage_embeddings(embeddings_file_path):
    if os.path.exists(embeddings_file_path):
        with open(embeddings_file_path, "rb") as f:
            storage_embeddings = pickle.load(f)
            return storage_embeddings
    return None


def indepth_document_fields(array_json_array_document_fields, pdf_path):
    embeddings_file_path = get_embeddings_file_path(pdf_path)
    pdf_storage_embeddings = get_existing_storage_embeddings(embeddings_file_path)
    number_related_chunks = 1
    for json_array_document_fields in array_json_array_document_fields:
        for document_field in json_array_document_fields:
            document_field['relevant_information'] = get_related_information(
                pdf_storage_embeddings,
                utils.dictionary_to_string(document_field),
                number_related_chunks
            )


def get_related_information(storage_embeddings, document_field, number_related_chunks):
    # search the K information most useful to answer to the query
    related_chunks = storage_embeddings.similarity_search(
        query=document_field,
        k=number_related_chunks
    )

    related_chunks_text = ""
    for related_chunk in related_chunks:
        related_chunks_text += related_chunk.page_content

    return related_chunks_text
