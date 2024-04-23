# ai_utils.py

import os
import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

from business_logic.prompts import generate_sbe_fields_prompt
from business_logic.prompts import generate_document_fields_prompt
from business_logic.prompts import generate_repeating_groups_prompt


def clean_json_string(json_string):
    cleaned_str = json_string.strip()
    cleaned_str = cleaned_str.replace("```json\n", "", 1)
    cleaned_str = cleaned_str.rsplit("\n```", 1)[0]

    return cleaned_str


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
