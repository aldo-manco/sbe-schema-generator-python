# app.py

import cv2
import layoutparser as lp
import numpy as np
import os
from pdf2image import convert_from_path
from PIL import Image
import json
#from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

import utils


def convert_pdf_pages_to_jpg(pdf_path, starting_page, ending_page, folder_path):
    try:
        if starting_page > ending_page:
            raise ValueError("Starting page cannot be greater than ending page.")
        utils.create_directory_if_not_exists(folder_path)

        array_images = convert_from_path(pdf_path, first_page=starting_page, last_page=ending_page)
        page_offset = 0
        for image in array_images:
            current_page = starting_page + page_offset
            print(current_page)
            image_path = os.path.join(folder_path, f"page_{current_page}.jpg")
            image.save(image_path, 'JPEG')
            page_offset = page_offset + 1

        print(f"Pages from {starting_page} to {ending_page} have been converted to JPEG and saved in {folder_path}")

    except Exception as e:
        print(f"Error during PDF to JPEG conversion: {e}")


def increase_contrast(image, image_path):
    # Crea un oggetto CLAHE (adattamento del contrasto limitato adattivo)
    bw_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(bw_image)

    cv2.imwrite(image_path, clahe_image)

    return image_path


def thresholding(image, image_path):

    bw_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Applica la soglia di Otsu per la binarizzazione
    _, otsu_image = cv2.threshold(
        bw_image,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    adaptive_image = cv2.adaptiveThreshold(
        bw_image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        19,  # Block Size: 15, 17, 19
        10  # C-Value: 5, 10
    )

    cv2.imwrite(image_path, otsu_image)

    return image_path


def detect_tables(image, output_previous_function):
    model = lp.Detectron2LayoutModel(
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

    layout = model.detect(image)

    return lp.Layout([element for element in layout if element.type == 'Table'])


def ocr_tables(image, layout_tables):
    ocr_agent = lp.TesseractAgent(languages='eng')

    for table in layout_tables:
        segment_image = (
            table
            # .pad(left=5, right=5, top=5, bottom=5)
            .crop_image(image)
        )

        text = ocr_agent.detect(segment_image)
        table.set(text=text, inplace=True)

    return layout_tables.get_texts()


def generate_document_fields(image, array_raw_document_fields):

    system_message = """
Sei un esperto di electronic trading systems con una conoscenza approfondita dei protocolli FIX e SBE. Ti verrà fornita in input una trascrizione grezza ottenuta tramite OCR di una tabella che rappresenta i campi di un messaggio FIX o SBE. La tua missione è ricostruire la tabella step by step seguendo i seguenti passaggi:
1. Definire quali sono le colonne della tabella.
2. Definire per ogni campo della tabella quali sono i valori delle colonne.
3. Creare un JSON array contenente un JSON object per ogni campo della tabella. Ogni JSON object conterrà delle coppie chiave/valore in cui la chiave corrisponde al nome della colonna e il valore corrisponde al valore della colonna per il campo specifico che il JSON object rappresenta.
Assicurati di includere solo ed esclusivamente il codice JSON. con le informazioni richieste seguendo gli esempi forniti.
    """

    example_1_human_message = """
### ESEMPIO 1: INPUT ###

    """

    example_1_assistant_message = """
### ESEMPIO 1: OUTPUT ###

    """

    example_2_human_message = """
### ESEMPIO 2: INPUT ###

    """

    example_2_assistant_message = """
### ESEMPIO 2: OUTPUT ###

    """

    example_3_human_message = """
### ESEMPIO 3: INPUT ###

    """

    example_3_assistant_message = """
### ESEMPIO 3: OUTPUT ###


    """

    human_message = """
### INPUT DELLO SVILUPPATORE ###
    """

    for raw_document_field in array_raw_document_fields:
        human_message += f"{raw_document_field} "

    human_message += """
### OUTPUT JSON CON LE INFORMAZIONI RICHIESTE ###
    """

    # ai_model = ChatOpenAI(
    #     openai_api_key=utils.openai_api_key,
    #     model=utils.ai_model_name,
    #     temperature=0,
    #     top_p=0
    # )
    #
    # array_document_fields = ai_model([
    #     SystemMessage(content=replace_newlines_with_space(system_message)),
    #     HumanMessage(content=example_1_human_message),
    #     AIMessage(content=example_1_assistant_message),
    #     HumanMessage(content=example_2_human_message),
    #     AIMessage(content=example_2_assistant_message),
    #     HumanMessage(content=example_3_human_message),
    #     AIMessage(content=example_3_assistant_message),
    #     HumanMessage(content=replace_newlines_with_space(human_message))
    # ])

    #return json.loads(array_document_fields.content)
    with open('a.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_fields(image, array_document_fields):
    # array_sbe_fields = []
    # for document_field in array_document_fields:
    #     sbe_field = generate_sbe_field(document_field)
    #     array_sbe_fields.append(sbe_field)
    # return array_sbe_fields
    with open('b.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_field(document_field):
    system_message = """
Sei un esperto di electronic trading systems con una profonda conoscenza dei protocolli FIX e SBE. La tua missione è assistere un utente nell'identificare varie caratteristiche riguardo un campo di un messaggio, basandoti sulle informazioni fornite dalla documentazione di un mercato.

Ecco i passaggi per determinare le informazioni richieste su ogni campo:
1. ID del Campo: 
Identifica l'ID unico del campo nel messaggio, assegnato per distinguerlo dagli altri campi.
2. Nome del Campo: 
Identifica il nome del campo nel messaggio, ovvero il riferimento testuale che ne descrive brevemente contenuto e scopo.
3. Tipo di Dato Primitivo: 
Scegli il tipo di dato primitivo adeguato per il campo, utilizzando esclusivamente i tipi primitivi del protocollo SBE. Ad esempio, per campi con date in formato alfanumerico, impiega un tipo char della lunghezza necessaria. Se il campo presenta un numero limitato di opzioni, usa un'enumerazione (nome del campo in camelCase + "_enum") se si può selezionare solo un valore, o un set (nome del campo in camelCase + "_set") se sono selezionabili più valori.
4. Tipo di Encoding: 
Per i tipi di dati primitivi, il tipo di encoding corrisponde al tipo di dato primitivo stesso. Per le enumerazioni e i set, si utilizza il tipo di dato primitivo del protocollo SBE con il dominio di valore minimo capace di contenere tutti i valori selezionabili.
5. Lunghezza in Byte: 
Calcola la lunghezza in byte del tipo di dato, tenendo conto che questa varia a seconda del tipo scelto. Ad esempio, un char occupa generalmente 1 byte. Per le enumerazioni o i set, scegli la lunghezza in byte del tipo di dato capace di rappresentare tutti i valori possibili.
6. Obbligatorio/Facoltativo: 
Determina se il campo è obbligatorio o facoltativo, stabilendo se deve essere sempre incluso o se può essere omesso in alcuni messaggi.
7. Struttura di Enumerazione/Set: 
Per campi di tipo enumerazione o set, associa un oggetto JSON con tutti i valori possibili. Se il tipo di dato è primitivo, usa un JSON vuoto {}.

Assicurati di includere solo ed esclusivamente il codice JSON con le informazioni richieste seguendo gli esempi forniti.
    """

    example_1_human_message = """
### ESEMPIO 1: INPUT ###

{
  "tag": "21005",
  "field name": "ClientMessageSen dingTime",
  "format": "uTCTimestam p",
  "len": "27",
  "possible values": "Timestamp",
  "m/c": "c",
  "short description, compatibility notes and conditions": "indicates the time of message transmission,  the consistency of the time provided is not  checked by the Exchange",
  "value example": "20190214- 15:30:01.4 62743346"
}
    """

    example_1_assistant_message = """
### ESEMPIO 1: OUTPUT ###

{
  "field_id": 21005,
  "field_name": "ClientMessageSendingTime",
  "data_type": "char",
  "encoding_type": "char",
  "length": 27,
  "presence": "optional",
  "structure": {}
}
    """

    example_2_human_message = """
### ESEMPIO 2: INPUT ###

{
    "tag": "21013",
    "field name": "AckPhase",
    "format": "Char",
    "len": "1",
    "possible values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "m/c": "a",
    "short description, compatibility notes and conditions": "indicates the trading phase during which  the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "value example": "1"
}
    """

    example_2_assistant_message = """
### ESEMPIO 2: OUTPUT ###

{
  "field_id": 21013,
  "field_name": "AckPhase",
  "data_type": "AckPhase_enum",
  "encoding_type": "int8",
  "length": 1,
  "presence": "mandatory",
  "structure": {
    "1": "Continuous Trading Phase",
    "2": "Call Phase",
    "3": "Halt Phase",
    "5": "Trading At Last Phase",
    "6": "Reserved",
    "7": "Suspended",
    "8": "Random"
  }
}
    """

    example_3_human_message = """
### ESEMPIO 3: INPUT ###

{
    "tag": "7443",
    "field name": "PostingAction",
    "format": "MultipleCharV alue",
    "len": "19",
    "possible values": "0 = Field Actively Used 1 = Leg 1 2 = Leg 2 3 = Leg 3 4 = Leg 4 5 = Leg 5 6 = Leg 6 7 = Leg 7 8 = Leg 8 9 = Leg 9",
    "m/c": "o",
    "short description, compatibility notes and conditions": "posting action code (Open/Close) for the  order.  Populated in Drop Copy only if provided on  order entry by the client. Only positions 0 and 1 apply for the Cash  markets",
    "value example": "0 0 0 0 0 0  0 0 0 0"
}
    """

    example_3_assistant_message = """
### ESEMPIO 3: OUTPUT ###

{
  "field_id": 7443,
  "field_name": "PostingAction",
  "data_type": "PostingAction_set",
  "encoding_type": "int8",
  "length": 1,
  "presence": "optional",
  "structure": {
    "0": "Field Actively Used",
    "1": "Leg 1",
    "2": "Leg 2",
    "3": "Leg 3",
    "4": "Leg 4",
    "5": "Leg 5",
    "6": "Leg 6",
    "7": "Leg 7",
    "8": "Leg 8",
    "9": "Leg 9"
  }
}
    """

    human_message = f"""
### INPUT DELLO SVILUPPATORE ###

{document_field}

### OUTPUT JSON CON LE INFORMAZIONI RICHIESTE ###
    """

    ai_model = ChatOpenAI(
        openai_api_key=utils.openai_api_key,
        model=utils.ai_model_name,
        temperature=0,
        top_p=0
    )

    json_sbe_field = ai_model([
        SystemMessage(content=replace_newlines_with_space(system_message)),
        HumanMessage(content=example_1_human_message),
        AIMessage(content=example_1_assistant_message),
        HumanMessage(content=example_2_human_message),
        AIMessage(content=example_2_assistant_message),
        HumanMessage(content=example_3_human_message),
        AIMessage(content=example_3_assistant_message),
        HumanMessage(content=human_message)
    ])

    return json.loads(json_sbe_field.content)


def replace_newlines_with_space(input_string):
    return input_string.replace('\n', ' ')


def process(pdf_path, starting_page, ending_page, folder_path="extracted_pdf_pages"):
    convert_pdf_pages_to_jpg(pdf_path, starting_page, ending_page, folder_path)

    array_complete_sbe_fields = []

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(folder_path, file_name)
        image = cv2.imread(image_path)
        image = image[..., ::-1]

        data = image_path
        pipeline_functions = [
            #increase_contrast,
            #thresholding,
            detect_tables,
            ocr_tables,
            generate_document_fields,
            generate_sbe_fields
        ]

        i = 1
        for function in pipeline_functions:
            try:
                data = function(image, data)
                print(i)
                i = i + 1
            except FileNotFoundError as e:
                print(e)
            except Exception as e:
                print(f"Errore nel processare l'immagine {file_name}: {e}")

        array_complete_sbe_fields.extend(data)

    with open('proof_data.txt', 'a', encoding="utf-8") as file:
        for data in array_complete_sbe_fields:
            file.write(f"{data}\n")


if __name__ == "__main__":
    process("drop_copy_service.pdf", 23, 24, "extracted_pdf_pages")
