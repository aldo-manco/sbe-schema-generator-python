# ai_engine_module.py

import cv2
import layoutparser as lp
import os
from pdf2image import convert_from_path
import json
import multiprocessing
from multiprocessing import Pool
from dotenv import load_dotenv
import logging
from PyPDF2 import PdfReader

from utils import utils
from utils import cv_utils
from utils import ai_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_pdf_pages_to_jpg(input_pipeline):
    try:
        pdf_path = input_pipeline['pdf_path']
        starting_page = input_pipeline['starting_page']
        ending_page = input_pipeline['ending_page']

        if starting_page > ending_page:
            raise ValueError("Starting page cannot be greater than ending page.")

        folder_name = "extracted_pdf_pages"
        subfolder_name = f"{starting_page}_{ending_page}"
        folder_path = os.path.join(folder_name, subfolder_name)
        utils.create_directory_if_not_exists(folder_path)

        array_images = convert_from_path(
            pdf_path,
            first_page=starting_page,
            last_page=ending_page
        )

        array_image_paths = []

        page_offset = 0
        for image in array_images:
            current_page = starting_page + page_offset
            image_path = os.path.join(folder_path, f"page_{current_page}.jpg")
            array_image_paths.append(image_path)
            image.save(image_path, 'JPEG')
            page_offset = page_offset + 1

        print(
            f"Pages from {starting_page} to {ending_page} have been converted to JPEG and saved in {folder_path}")

        return {
            "array_image_paths": array_image_paths
        }

    except Exception as e:
        print(f"Error during PDF to JPEG conversion: {e}")


def grayscale_batch_processing(output_previous_function):
    array_image_paths = output_previous_function["array_image_paths"]

    number_processes = utils.get_number_processes(array_image_paths)

    with Pool(processes=number_processes) as pool:
        array_grayscale_images = pool.map(cv_utils.convert_grayscale, array_image_paths)

    return {
        "array_images_info": array_grayscale_images
    }


def increase_contrast_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

    number_processes = utils.get_number_processes(array_images_info)

    with Pool(processes=number_processes) as pool:
        array_contrast_images_info = pool.map(cv_utils.increase_contrast, array_images_info)

    return {
        "array_images_info": array_contrast_images_info
    }


def thresholding_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

    number_processes = utils.get_number_processes(array_images_info)

    with Pool(processes=number_processes) as pool:
        array_binary_images_info = pool.map(thresholding, array_images_info)

    return {
        "array_images_info": array_binary_images_info
    }


def table_detection_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

    detectron2_model = lp.Detectron2LayoutModel(
        config_path='../config.yaml',
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
        label_map={
            0: "Text",
            1: "Title",
            2: "List",
            3: "Table",
            4: "Figure"
        }
    )

    array_layout_pages = []

    for image_info in array_images_info:
        image_page = image_info["image"]
        image_page_rgb = cv2.cvtColor(image_page, cv2.COLOR_GRAY2RGB)

        layout = detectron2_model.detect(image_page_rgb)
        array_layout_tables = lp.Layout([element for element in layout if element.type == 'Table'])

        array_layout_pages.append({
            "image_page": image_page,
            "array_layout_tables": array_layout_tables
        })

    return {
        "array_layout_pages": array_layout_pages
    }


def ocr_tables_batch_processing(output_previous_function):
    array_layout_pages = output_previous_function["array_layout_pages"]

    tesseract_model = lp.TesseractAgent(languages='eng')

    array_text_tables_pages = []

    for layout_page in array_layout_pages:

        image_page = layout_page["image_page"]
        array_layout_tables = layout_page["array_layout_tables"]

        for layout_table in array_layout_tables:
            image_table = (
                layout_table
                # .pad(left=5, right=5, top=5, bottom=5)
                .crop_image(image_page)
            )

            text = tesseract_model.detect(image_table)
            layout_table.set(text=text, inplace=True)

        array_text_tables_pages.append('\n'.join(array_layout_tables.get_texts()))

    return {
        "array_pdf_pages_texts": array_text_tables_pages
    }


def extract_pdf_text(input_pipeline):
    pdf_path = input_pipeline['pdf_path']
    starting_page = input_pipeline['starting_page']
    ending_page = input_pipeline['ending_page']

    pdf_reader = PdfReader(pdf_path)
    number_pdf_pages = len(pdf_reader.pages)

    array_page_info = [(pdf_path, page) for page in range(number_pdf_pages)]

    number_processes = utils.get_number_processes(array_page_info)
    with multiprocessing.Pool(number_processes) as pool:
        array_pdf_pages_texts = pool.map(cv_utils.extract_page_text, array_page_info)

    chunk_size = 500
    chunk_overlap = 200

    ai_utils.create_storage_embeddings(
        pdf_path,
        array_pdf_pages_texts,
        chunk_size,
        chunk_overlap
    )

    return {
        "array_pdf_pages_texts": array_pdf_pages_texts[starting_page:ending_page + 1],
        "pdf_path": pdf_path
    }


def group_multiple_pages_texts(output_previous_function):
    array_pdf_pages_texts = output_previous_function["array_pdf_pages_texts"]
    pdf_path = output_previous_function["pdf_path"]

    array_grouped_text_tables_pages = utils.group_texts_in_array(
        array_pdf_pages_texts,
        2
    )

    return {
        "array_pdf_pages_texts": array_grouped_text_tables_pages,
        "pdf_path": pdf_path
    }


def document_fields_generation_batch_processing(output_previous_function):
    array_pdf_pages_texts = output_previous_function["array_pdf_pages_texts"]
    pdf_path = output_previous_function["pdf_path"]

    number_processes = utils.get_number_processes(array_pdf_pages_texts)

    with Pool(processes=number_processes) as pool:
        array_json_array_document_fields = pool.map(ai_utils.generate_document_fields, array_pdf_pages_texts)

    max_group_size = 10

    optimized_array_json_array_document_fields = utils.generate_optimal_array_of_json_array(
        array_json_array_document_fields,
        max_group_size
    )

    utils.numbering_document_fields(
        optimized_array_json_array_document_fields,
    )

    logging.info(f"optimized_array_json_array_document_fields: {optimized_array_json_array_document_fields}")

    ai_utils.indepth_document_fields(
        optimized_array_json_array_document_fields,
        pdf_path
    )

    logging.info(f"optimized_array_json_array_document_fields: {optimized_array_json_array_document_fields}")

    # with open('business_logic/testing/ai_document_fields.json', 'r') as file:
    #     optimized_array_json_array_document_fields = json.load(file)

    return {
        "array_json_array_document_fields": optimized_array_json_array_document_fields
    }


def generate_sbe_message_components(output_previous_function):
    array_json_array_document_fields = output_previous_function["array_json_array_document_fields"]

    number_processes = utils.get_number_processes(array_json_array_document_fields)
    with Pool(number_processes) as pool:
        array_json_array_sbe_fields = pool.map(ai_utils.generate_sbe_fields, array_json_array_document_fields)

    # with open('business_logic/testing/ai_sbe_fields.json', 'r') as file:
    #     array_json_array_sbe_fields = json.load(file)

    json_array_full_sbe_fields = utils.merge_unique_sbe_fields_json_arrays(array_json_array_sbe_fields)

    number_processes = utils.get_number_processes(array_json_array_document_fields)
    with Pool(number_processes) as pool:
        if len(array_json_array_document_fields) == 1:
            array_json_array_repeating_groups = pool.map(
                ai_utils.generate_repeating_groups,
                array_json_array_document_fields
            )
        else:
            array_splitted_json_array_document_fields = utils.split_json_arrays(array_json_array_document_fields)
            array_document_fields_adjacent_pages = [
                (array_splitted_json_array_document_fields[i] + array_splitted_json_array_document_fields[i + 1]) for i
                in
                range(len(array_splitted_json_array_document_fields) - 1)
            ]
            array_json_array_repeating_groups = pool.map(
                ai_utils.generate_repeating_groups,
                array_document_fields_adjacent_pages
            )

    # with open('business_logic/testing/ai_repeating_groups.json', 'r') as file:
    #     array_json_array_repeating_groups = json.load(file)

    json_array_distinct_repeating_groups = utils.merge_unique_repeating_groups_json_arrays(
        array_json_array_repeating_groups
    )

    if len(json_array_distinct_repeating_groups) <= 0:
        return json_array_full_sbe_fields, []

    array_repeating_group_field_ai_engine_ids = utils.get_ai_engine_ids_repeating_groups(
        json_array_distinct_repeating_groups
    )

    utils.fill_array_repeating_groups_with_sbe_fields(
        json_array_distinct_repeating_groups,
        json_array_full_sbe_fields
    )

    logging.info(
        f"json_array_distinct_repeating_groups: {json_array_distinct_repeating_groups}")

    json_array_sbe_fields = utils.get_array_sbe_fields_outside_repeating_groups(
        json_array_full_sbe_fields,
        array_repeating_group_field_ai_engine_ids
    )

    logging.info(f"json_array_sbe_fields: {json_array_sbe_fields}")

    return json_array_sbe_fields, json_array_distinct_repeating_groups


def execute_pipeline_filters(pipeline_filters, input_pipeline):
    data = input_pipeline
    i = 1
    for function in pipeline_filters:
        try:
            data = function(data)
            logger.info(f"Filter #{i} Completed Successfully")
            i = i + 1
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Errore nel processare il #{i} filtro: {e}")

    return data


def process(pdf_path, starting_page, ending_page, is_pdf_editable):
    load_dotenv()

    input_pipeline = {
        "pdf_path": pdf_path,
        "starting_page": starting_page,
        "ending_page": ending_page
    }

    read_only_pdf_pipeline_filters = [
        convert_pdf_pages_to_jpg,
        grayscale_batch_processing,
        increase_contrast_batch_processing,
        thresholding_batch_processing,
        table_detection_batch_processing,
        ocr_tables_batch_processing,
        group_multiple_pages_texts,
        document_fields_generation_batch_processing,
        generate_sbe_message_components
    ]

    editable_pdf_pipeline_filters = [
        extract_pdf_text,
        group_multiple_pages_texts,
        document_fields_generation_batch_processing,
        generate_sbe_message_components
    ]

    if is_pdf_editable:
        return execute_pipeline_filters(
            editable_pdf_pipeline_filters,
            input_pipeline
        )
    else:
        return execute_pipeline_filters(
            read_only_pdf_pipeline_filters,
            input_pipeline
        )


if __name__ == "__main__":
    process("pdf_documents/euronext_mdg.pdf", 74, 74, True)
