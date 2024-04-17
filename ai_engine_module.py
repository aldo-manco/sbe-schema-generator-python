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

    array_page_info = [(pdf_path, page) for page in range(starting_page - 1, ending_page)]

    number_processes = utils.get_number_processes(array_page_info)
    with multiprocessing.Pool(number_processes) as pool:
        array_text_pages = pool.map(extract_page_text, array_page_info)

    return {
        "array_text_pages": array_text_pages
    }


def extract_page_text(page_info):
    pdf_path, page_number = page_info
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_number)
        text = page.get_text()
    return text


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
        array_grayscale_images = pool.map(convert_grayscale, array_image_paths)

    return {
        "array_images_info": array_grayscale_images
    }


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


def increase_contrast_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

    number_processes = utils.get_number_processes(array_images_info)

    with Pool(processes=number_processes) as pool:
        array_contrast_images_info = pool.map(increase_contrast, array_images_info)

    return {
        "array_images_info": array_contrast_images_info
    }


def increase_contrast(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image_clahe = clahe.apply(image)

    cv2.imwrite(image_path, image_clahe)

    return {
        "image_path": image_path,
        "image": image_clahe
    }


def thresholding_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

    number_processes = utils.get_number_processes(array_images_info)

    with Pool(processes=number_processes) as pool:
        array_binary_images_info = pool.map(thresholding, array_images_info)

    return {
        "array_images_info": array_binary_images_info
    }


def thresholding(output_previous_function):
    image_path = output_previous_function["image_path"]
    image = output_previous_function["image"]

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


def table_detection_batch_processing(output_previous_function):
    array_images_info = output_previous_function["array_images_info"]

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
        "array_text_pages": array_text_tables_pages
    }


def group_multiple_pages_texts(output_previous_function):
    array_text_pages = output_previous_function["array_text_pages"]
    array_grouped_text_tables_pages = utils.group_texts_in_array(
        array_text_pages,
        2
    )

    return {
        "array_text_pages": array_grouped_text_tables_pages
    }


def document_fields_generation_batch_processing(output_previous_function):
    array_text_pages = output_previous_function["array_text_pages"]

    number_processes = utils.get_number_processes(array_text_pages)

    with Pool(processes=number_processes) as pool:
        array_json_array_document_fields = pool.map(generate_document_fields, array_text_pages)

    optimized_array_json_array_document_fields = utils.generate_optimal_array_of_json_array(
        array_json_array_document_fields,
        15
    )

    return {
        "array_json_array_document_fields": optimized_array_json_array_document_fields
    }


def generate_document_fields(array_text_pages):
    human_message = f"""
### INPUT ###

{array_text_pages}

### OUTPUT JSON ###
        """

    output = utils.get_output_from_generative_ai(
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
    # output = "[]"

    logging.info(f"\n\nDOCUMENT FIELDS: {output}\n\n")

    return json.loads(output)

    # with open('ai_document_fields.json', 'r') as file:
    #     data = json.load(file)
    #
    # return data


def generate_repeating_groups(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
    """

    output = utils.get_output_from_generative_ai(
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
    # output = "[]"

    logging.info(f"\n\nREPEATING GROUPS: {output}\n\n")

    return json.loads(output)

    # with open('ai_repeating_groups.json', 'r') as file:
    #     data = json.load(file)
    #
    # return data


def generate_sbe_fields(array_document_fields):
    string_array_document_fields = json.dumps(array_document_fields)

    human_message = f"""
### INPUT ###

{string_array_document_fields}

### OUTPUT JSON ###
        """

    output = utils.get_output_from_generative_ai(
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
    # output = "[]"

    logging.info(f"\n\nSBE FIELDS: {output}\n\n")

    return json.loads(output)

    # with open('ai_sbe_fields.json', 'r') as file:
    #     data = json.load(file)
    #
    # return data


def generate_sbe_message_components(output_previous_function):
    array_json_array_document_fields = output_previous_function["array_json_array_document_fields"]

    # SBE FIELDS
    number_processes = utils.get_number_processes(array_json_array_document_fields)
    with Pool(number_processes) as pool:
        array_json_array_sbe_fields = pool.map(generate_sbe_fields, array_json_array_document_fields)

    json_array_full_sbe_fields = utils.merge_unique_json_arrays(array_json_array_sbe_fields)

    # REPEATING GROUPS
    json_array_repeating_groups = []

    number_processes = utils.get_number_processes(array_json_array_document_fields)
    with Pool(number_processes) as pool:
        if len(array_json_array_document_fields) == 1:
            array_json_array_repeating_groups = pool.map(
                generate_repeating_groups,
                array_json_array_document_fields
            )
        else:
            array_splitted_json_array_document_fields = utils.split_json_arrays(array_json_array_document_fields)
            array_document_fields_adjacent_pages = [
                (array_splitted_json_array_document_fields[i] + array_splitted_json_array_document_fields[i + 1]) for i in
                range(len(array_splitted_json_array_document_fields) - 1)]
            array_json_array_repeating_groups = pool.map(
                generate_repeating_groups,
                array_document_fields_adjacent_pages
            )

    # FILTERING SBE FIELDS
    json_array_full_repeating_groups = utils.merge_unique_json_arrays(array_json_array_repeating_groups)
    if len(json_array_full_repeating_groups) > 0:

        for json_array_repeating_group in array_json_array_repeating_groups:
            for repeating_group in json_array_repeating_group:
                if not utils.is_duplicate_in_json_array(
                        "group_id",
                        repeating_group["group_id"],
                        json_array_repeating_groups
                ):
                    json_array_repeating_groups.append(repeating_group)

        array_json_array_repeating_groups_document_fields = [repeating_group["items"] for repeating_group in
                                                             json_array_repeating_groups]

        number_processes = utils.get_number_processes(json_array_repeating_groups)
        with Pool(number_processes) as pool:
            array_json_array_repeating_groups_sbe_fields = pool.map(generate_sbe_fields,
                                                                    array_json_array_repeating_groups_document_fields)

        ids_to_remove = set()
        names_to_remove = set()

        for i, repeating_group in enumerate(json_array_repeating_groups):
            repeating_group["items"] = array_json_array_repeating_groups_sbe_fields[i]
            ids_to_remove.add(repeating_group["group_id"])
            names_to_remove.add(repeating_group["group_name"])
            for group_sbe_field in repeating_group["items"]:
                ids_to_remove.add(group_sbe_field["field_id"])
                names_to_remove.add(group_sbe_field["field_name"])

        json_array_sbe_fields = []

        for field in json_array_full_sbe_fields:
            if field["field_id"] not in ids_to_remove and field["field_name"] not in names_to_remove:
                json_array_sbe_fields.append(field)

        return json_array_sbe_fields, json_array_repeating_groups

    return json_array_full_sbe_fields, json_array_repeating_groups


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
    process("pdf_documents/drop_copy_service.pdf", 24, 26, False)
