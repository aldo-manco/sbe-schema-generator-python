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
import sys
import fitz

import utils
from prompts import generate_document_fields_prompt
from prompts import generate_repeating_groups_prompt
from prompts import generate_sbe_fields_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_pdf_text(input_pipeline):
    pdf_path = input_pipeline['pdf_path']
    starting_page = input_pipeline['starting_page']
    ending_page = input_pipeline['ending_page']

    num_pages = ending_page - starting_page + 1
    num_processes = min(multiprocessing.cpu_count(), num_pages)

    array_text_tables_pages = []

    with multiprocessing.Pool(num_processes) as pool:
        params = [(pdf_path, page) for page in range(starting_page, ending_page + 1)]
        array_text_tables_pages.append({
            "text_tables": pool.map(extract_page_text, params)
        })

    return array_text_tables_pages


def extract_page_text(args):
    pdf_path, page_number = args
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_number)
        text = page.get_text()
    return text


def convert_pdf_pages_to_jpg(input_pipeline):
    try:
        array_file_names = [file for file in os.listdir(input_pipeline["folder_path"]) if file.endswith(('.jpg', '.jpeg', '.png'))]
        array_image_paths = []
        for file_name in array_file_names:
            image_path = os.path.join(input_pipeline["folder_path"], file_name)
            array_image_paths.append(image_path)

        if input_pipeline["starting_page"] > input_pipeline["ending_page"]:
            raise ValueError("Starting page cannot be greater than ending page.")
        utils.create_directory_if_not_exists(input_pipeline["folder_path"])

        array_images = convert_from_path(input_pipeline["pdf_path"], first_page=input_pipeline["starting_page"], last_page=input_pipeline["ending_page"])
        page_offset = 0
        for image in array_images:
            current_page = input_pipeline["starting_page"] + page_offset
            print(current_page)
            image_path = os.path.join(input_pipeline["folder_path"], f"page_{current_page}.jpg")
            image.save(image_path, 'JPEG')
            page_offset = page_offset + 1

        print(f"Pages from {input_pipeline['starting_page']} to {input_pipeline['ending_page']} have been converted to JPEG and saved in {input_pipeline['folder_path']}")

        return {
            "array_image_paths": array_image_paths
        }

    except Exception as e:
        print(f"Error during PDF to JPEG conversion: {e}")


def grayscale_batch_processing(output_previous_function):
    number_processes = min(multiprocessing.cpu_count(), len(output_previous_function["array_image_paths"]))
    array_grayscale_images = []

    with Pool(processes=number_processes) as pool:
        array_grayscale_images = pool.map(convert_grayscale, output_previous_function["array_image_paths"])

    return array_grayscale_images


def convert_grayscale(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("L'immagine specificata non è stata trovata.")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

        return {
            "image_path": image_path,
            "image": image_gray
        }

    except Exception as e:
        print(f"Si è verificato un errore durante la conversione dell'immagine: {e}")
        return None


def increase_contrast_batch_processing(array_output_previous_function):
    number_processes = min(multiprocessing.cpu_count(), len(array_output_previous_function))
    array_contrast_images = []

    with Pool(processes=number_processes) as pool:
        array_contrast_images = pool.map(increase_contrast, array_output_previous_function)

    return array_contrast_images


def increase_contrast(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

    # Crea un oggetto CLAHE (adattamento del contrasto limitato adattivo)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image_clahe = clahe.apply(image)

    cv2.imwrite(image_path, image_clahe)

    return {
        "image_path": image_path,
        "image": image_clahe
    }


def thresholding_batch_processing(array_output_previous_function):
    number_processes = min(multiprocessing.cpu_count(), len(array_output_previous_function))
    array_binary_images = []

    with Pool(processes=number_processes) as pool:
        array_binary_images = pool.map(thresholding, array_output_previous_function)

    return array_binary_images


def thresholding(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

    # Applica la soglia di Otsu per la binarizzazione
    _, image_otsu = cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    image_adaptive = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        19,  # Block Size: 15, 17, 19
        10  # C-Value: 5, 10
    )

    cv2.imwrite(image_path, image_otsu)

    return {
        "image_path": image_path,
        "image": image_otsu
    }


def table_detection_batch_processing(array_output_previous_function):
    detectron2_model = lp.Detectron2LayoutModel(
        config_path='config.yaml',
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.65],
        label_map={
            0: "Text",
            1: "Title",
            2: "List",
            3: "Table",
            4: "Figure"
        }
    )

    array_layout_tables = []

    for output_previous_function in array_output_previous_function:
        image = output_previous_function["image"]
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        layout = detectron2_model.detect(image_rgb)
        layout_tables = lp.Layout([element for element in layout if element.type == 'Table'])

        array_layout_tables.append({
            "image": image,
            "layout_tables": layout_tables
        })

    return array_layout_tables


def ocr_tables_batch_processing(array_output_previous_function):
    tesseract_model = lp.TesseractAgent(languages='eng')

    array_text_tables_pages = []

    for output_previous_function in array_output_previous_function:

        image = output_previous_function["image"]
        layout_tables = output_previous_function["layout_tables"]

        for table in layout_tables:
            image_cropped = (
                table
                # .pad(left=5, right=5, top=5, bottom=5)
                .crop_image(image)
            )

            text = tesseract_model.detect(image_cropped)
            table.set(text=text, inplace=True)

            array_text_tables_pages.append({
                "text_tables": layout_tables.get_texts()
            })

    return array_text_tables_pages


def document_fields_generation_batch_processing(array_output_previous_function):
    number_processes = min(multiprocessing.cpu_count(), len(array_output_previous_function))
    array_json_array_document_fields = []

    with Pool(processes=number_processes) as pool:
        array_json_array_document_fields = pool.map(generate_document_fields, array_output_previous_function)

    return array_json_array_document_fields


def generate_document_fields(text_tables):
    human_message = f"""
### INPUT ###

{text_tables["text_tables"]}

### OUTPUT JSON ###
        """

    # output = utils.get_output_from_generative_ai(
    #     generate_document_fields_prompt.system_message,
    #     generate_document_fields_prompt.example_1_human_message,
    #     generate_document_fields_prompt.example_1_assistant_message,
    #     generate_document_fields_prompt.example_2_human_message,
    #     generate_document_fields_prompt.example_2_assistant_message,
    #     generate_document_fields_prompt.example_3_human_message,
    #     generate_document_fields_prompt.example_3_assistant_message,
    #     generate_document_fields_prompt.example_4_human_message,
    #     generate_document_fields_prompt.example_4_assistant_message,
    #     human_message
    # )
    #
    # with open('ai_document_fields.json', 'w') as file:
    #     file.write(output)
    #
    # logging.info(f"\noutput: {output}\n\n")
    #
    # return json.loads(output)

    with open('ai_document_fields.json', 'r') as file:
        data = json.load(file)

    return data


def generate_repeating_groups(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
    """

    # output = utils.get_output_from_generative_ai(
    #     generate_repeating_groups_prompt.system_message,
    #     generate_repeating_groups_prompt.example_1_human_message,
    #     generate_repeating_groups_prompt.example_1_assistant_message,
    #     generate_repeating_groups_prompt.example_2_human_message,
    #     generate_repeating_groups_prompt.example_2_assistant_message,
    #     generate_repeating_groups_prompt.example_3_human_message,
    #     generate_repeating_groups_prompt.example_3_assistant_message,
    #     generate_repeating_groups_prompt.example_4_human_message,
    #     generate_repeating_groups_prompt.example_4_assistant_message,
    #     human_message
    # )
    #
    # with open('ai_repeating_groups.json', 'a') as file:
    #     file.write(output)
    #
    # return json.loads(output)

    with open('ai_repeating_groups.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_fields(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
        """

    # output = utils.get_output_from_generative_ai(
    #     generate_sbe_fields_prompt.system_message,
    #     generate_sbe_fields_prompt.example_1_human_message,
    #     generate_sbe_fields_prompt.example_1_assistant_message,
    #     generate_sbe_fields_prompt.example_2_human_message,
    #     generate_sbe_fields_prompt.example_2_assistant_message,
    #     generate_sbe_fields_prompt.example_3_human_message,
    #     generate_sbe_fields_prompt.example_3_assistant_message,
    #     generate_sbe_fields_prompt.example_4_human_message,
    #     generate_sbe_fields_prompt.example_4_assistant_message,
    #     human_message
    # )
    #
    # with open('ai_sbe_fields.json', 'a') as file:
    #     file.write(output)
    #
    # return json.loads(output)

    with open('ai_sbe_fields.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_message_components(array_json_array_document_fields):
    json_array_repeating_groups = []

    number_processes = min(multiprocessing.cpu_count(), len(array_json_array_document_fields))
    with Pool(number_processes) as pool:
        if len(array_json_array_document_fields) == 1:
            array_json_array_repeating_groups = pool.map(generate_repeating_groups, array_json_array_document_fields)
        else:
            array_document_fields_adjacent_pages = [
                (array_json_array_document_fields[i] + array_json_array_document_fields[i + 1]) for i in
                range(len(array_json_array_document_fields) - 1)]
            array_json_array_repeating_groups = pool.map(generate_repeating_groups,
                                                         array_document_fields_adjacent_pages)

    for json_array_repeating_group in array_json_array_repeating_groups:
        for repeating_group in json_array_repeating_group:
            if not utils.is_duplicate_in_json_array("group_id", repeating_group["group_id"],
                                                    json_array_repeating_groups):
                json_array_repeating_groups.append(repeating_group)

    with Pool(number_processes) as pool:
        array_json_array_sbe_fields = pool.map(generate_sbe_fields, array_json_array_document_fields)

    json_array_full_sbe_fields = utils.merge_unique_json_arrays(array_json_array_sbe_fields)

    logging.info(f"json_array_repeating_groups: {json_array_repeating_groups}")

    with Pool(number_processes) as pool:
        array_json_array_repeating_groups_document_fields = [repeating_group["items"] for repeating_group in
                                                             json_array_repeating_groups]
        logging.info(
            f"array_json_array_repeating_groups_document_fields: {array_json_array_repeating_groups_document_fields}")
        array_json_array_repeating_groups_sbe_fields = pool.map(generate_sbe_fields,
                                                                array_json_array_repeating_groups_document_fields)
        logging.info(f"array_json_array_repeating_groups_sbe_fields: {array_json_array_repeating_groups_sbe_fields}")

    for i, repeating_group in enumerate(json_array_repeating_groups):
        repeating_group["items"] = array_json_array_repeating_groups_sbe_fields[i]

    ids_to_remove = set()
    names_to_remove = set()

    logging.info(f"json_array_repeating_groups: {json_array_repeating_groups}")

    for repeating_group in json_array_repeating_groups:
        for group_sbe_field in repeating_group["items"]:
            ids_to_remove.add(group_sbe_field["field_id"])
            names_to_remove.add(group_sbe_field["field_name"])

    json_array_sbe_fields = []

    logging.info(f"ids: {ids_to_remove}\n\n names: {names_to_remove}")

    for field in json_array_full_sbe_fields:
        if field["field_id"] not in ids_to_remove and field["field_name"] not in names_to_remove:
            json_array_sbe_fields.append(field)

    logging.info(f"json_array_sbe_fields: {json_array_sbe_fields}")

    return json_array_sbe_fields, json_array_repeating_groups


def execute_pipeline_filters(pipeline_filters, input_pipeline):
    data = input_pipeline
    i = 1
    for function in pipeline_filters:
        try:
            data = function(data)
            logger.info(f"num filter: {i}")
            i = i + 1
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Errore nel processare il #{i} filtro: {e}")

    return data


def process(pdf_path, starting_page, ending_page, folder_path="extracted_pdf_pages"):
    load_dotenv()

    input_pipeline = {
        "pdf_path": pdf_path,
        "starting_page": starting_page,
        "ending_page": ending_page,
        "folder_path": folder_path
    }

    pipeline_filters = [
        extract_pdf_text,
        #convert_pdf_pages_to_jpg,
        #grayscale_batch_processing,
        #increase_contrast_batch_processing,
        #thresholding_batch_processing,
        #table_detection_batch_processing,
        #ocr_tables_batch_processing,
        document_fields_generation_batch_processing,
        generate_sbe_message_components
    ]

    return execute_pipeline_filters(pipeline_filters, input_pipeline)


if __name__ == "__main__":
    process("pdf_documents/drop_copy_service.pdf", 26, 26, "extracted_pdf_pages")
