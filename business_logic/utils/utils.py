# utils.py

import logging
import os
import json
import math
from itertools import chain
import multiprocessing


def create_directory_if_not_exists(
        directory_path
):
    if not os.path.exists(directory_path):
        os.makedirs(
            directory_path
        )


def extract_pdf_filename(
        pdf_path
):
    base_name = os.path.basename(pdf_path)
    pdf_filename = os.path.splitext(base_name)[0]
    return pdf_filename


def save_uploaded_file(
        directory_path,
        file
):
    create_directory_if_not_exists(
        directory_path
    )
    file_path = os.path.join(
        directory_path,
        file.name
    )
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    return file_path


def merge_unique_sbe_fields_json_arrays(
        array_json_array
):
    unique_json_objects = set()
    merged_array = []

    for json_array in array_json_array:
        for json_object in json_array:
            json_str = json.dumps(
                json_object,
                sort_keys=True
            )

            if json_str not in unique_json_objects:
                unique_json_objects.add(
                    json_str
                )
                merged_array.append(
                    json_object
                )

    return merged_array


def get_index_intersected_group(
        new_repeating_group,
        array_repeating_groups
):
    new_repeating_group_items_set = set(
        new_repeating_group["items"]
    )

    for index, repeating_group in enumerate(array_repeating_groups, start=0):
        repeating_group_items_set = set(
            repeating_group["items"]
        )
        if bool(new_repeating_group_items_set & repeating_group_items_set):
            return index

    return -1


def merge_unique_repeating_groups_json_arrays(
        array_json_array_repeating_groups
):
    array_distinct_repeating_groups = []

    for array_repeating_groups in array_json_array_repeating_groups:
        for repeating_group in array_repeating_groups:
            index = get_index_intersected_group(
                repeating_group,
                array_distinct_repeating_groups
            )

            if index == -1:
                array_distinct_repeating_groups.append(
                    repeating_group
                )
            else:
                array_distinct_repeating_groups[index]["items"] += \
                    [id for id in repeating_group["items"]
                     if id not in array_distinct_repeating_groups[index]["items"]]

    return array_distinct_repeating_groups


def get_number_processes(
        array
):
    return max(
        min(
            multiprocessing.cpu_count(),
            len(array)
        ),
        1
    )


def group_texts_in_array(
        array_strings,
        number_elements
):
    array_grouped_strings = []

    grouped_strings = [
        array_strings[i:i + number_elements] for i in range(0, len(array_strings), number_elements)
    ]

    for group in grouped_strings:
        concatenated_string = ''.join(group)
        array_grouped_strings.append(
            concatenated_string
        )

    return array_grouped_strings


def split_json_arrays(array_of_json_arrays):
    array_splitted_json_arrays = []

    for json_array in array_of_json_arrays:
        if not isinstance(json_array, list):
            raise ValueError("Each item in the array must be a list.")

        split_index = len(json_array) // 2 + len(json_array) % 2

        first_part = json_array[:split_index]
        second_part = json_array[split_index:]

        array_splitted_json_arrays.append(
            first_part
        )
        array_splitted_json_arrays.append(
            second_part
        )

    return array_splitted_json_arrays


def merge_json_arrays(
        json_array_of_arrays
):
    return list(
        chain.from_iterable(json_array_of_arrays)
    )


def compute_optimal_group_size(
        total_items,
        max_group_size
):
    number_group = math.ceil(
        total_items / max_group_size
    )
    minimum_group_size = max_group_size

    for i in range(max_group_size - 1, 0, -1):
        if math.ceil(total_items / i) == number_group:
            minimum_group_size = i
        else:
            break

    return minimum_group_size


def group_json_objects(
        json_objects,
        group_size
):
    return [
        json_objects[i:i + group_size] for i in range(0, len(json_objects), group_size)
    ]


def generate_optimal_array_of_json_array(
        json_array_of_arrays,
        max_group_size
):
    merged_json_objects = merge_json_arrays(
        json_array_of_arrays
    )
    optimal_group_size = compute_optimal_group_size(
        len(merged_json_objects),
        max_group_size
    )
    grouped_json_objects = group_json_objects(
        merged_json_objects,
        optimal_group_size
    )

    return grouped_json_objects


def numbering_document_fields(
        array_json_array_document_fields
):
    ai_engine_id = 1
    for json_array_document_fields in array_json_array_document_fields:
        for document_field in json_array_document_fields:
            document_field['ai_engine_id'] = ai_engine_id
            ai_engine_id += 1


def dictionary_to_string(
        dictionary
):
    return ' and '.join(
        f'"{key}": "{value}"' for key, value in dictionary.items()
    )


def get_repeating_group_sbe_field(
        ai_engine_id,
        array_sbe_fields
):
    return next(
        filter(
            lambda sbe_field: sbe_field.get('ai_engine_id') == ai_engine_id,
            array_sbe_fields),
        None
    )


def get_ai_engine_ids_repeating_groups(
        array_repeating_groups
):
    array_ai_engine_ids = []

    for repeating_group in array_repeating_groups:
        for ai_engine_id in repeating_group["items"]:
            array_ai_engine_ids.append(ai_engine_id)
        for ai_engine_id in repeating_group["indicators_items"]:
            array_ai_engine_ids.append(ai_engine_id)

    return array_ai_engine_ids


def fill_array_repeating_groups_with_sbe_fields(
        array_repeating_groups,
        array_sbe_fields
):
    for repeating_group in array_repeating_groups:
        for index, repeating_group_field in enumerate(repeating_group["items"]):
            updated_repeating_group_field = get_repeating_group_sbe_field(
                repeating_group_field,
                array_sbe_fields
            )
            repeating_group["items"][index] = updated_repeating_group_field


def get_array_sbe_fields_outside_repeating_groups(
        json_array_full_sbe_fields,
        array_repeating_group_field_ai_engine_ids
):
    return [
        sbe_field for sbe_field in json_array_full_sbe_fields
        if sbe_field.get("ai_engine_id") not in array_repeating_group_field_ai_engine_ids
    ]
