# ai_engine_module.py

import cv2
import layoutparser as lp
import numpy as np
import os
from pdf2image import convert_from_path
from PIL import Image
import json
import multiprocessing
from functools import partial
# from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def detect_tables(output_previous_function):

    logging.info("det1")

    model_detectron2 = lp.Detectron2LayoutModel(
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

    logging.info("det2")

    image = output_previous_function["image"]
    image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    layout = model_detectron2.detect(image_rgb)
    layout_tables = lp.Layout([element for element in layout if element.type == 'Table'])

    logging.info("det3")

    return {
        "image": image,
        "layout_tables": layout_tables
    }


def ocr_tables(output_previous_function):

    model_tesseract = lp.TesseractAgent(languages='eng')

    image = output_previous_function["image"]
    layout_tables = output_previous_function["layout_tables"]

    logging.info("ocr1")

    for table in layout_tables:
        segment_image = (
            table
            # .pad(left=5, right=5, top=5, bottom=5)
            .crop_image(image)
        )

        text = model_tesseract.detect(segment_image)
        table.set(text=text, inplace=True)

    logging.info("ocr2")

    return {
        "text_tables": layout_tables.get_texts()
    }


def generate_document_fields(output_previous_function):
    text_tables = output_previous_function["text_tables"]

    system_message = """
Sei un esperto in sistemi di trading elettronico con una conoscenza approfondita dei protocolli FIX e SBE. Ti verra fornita in input una trascrizione grezza ottenuta tramite OCR di una tabella che rappresenta i campi di un messaggio FIX o SBE. La tua missione e ricostruire la tabella step by step seguendo i seguenti passaggi:
1. Definire quali sono le colonne della tabella.
2. Definire per ogni campo della tabella quali sono i valori delle colonne.
3. Creare un JSON array contenente un JSON object per ogni campo della tabella. Ogni JSON object conterra delle coppie chiave/valore in cui la chiave corrisponde al nome della colonna e il valore corrisponde al valore della colonna per il campo specifico che il JSON object rappresenta.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun campo del messaggio, un oggetto JSON con le informazioni fornite. Segui gli esempi che ti sono stati forniti.
        """

    example_1_human_message = """
Tag Field Name Format Len Possible Values M/C | Short Description, Compatibility Notes Value
& Conditions Example
21005 | ClientMessageSen | UTCTimestam 27 | Timestamp Cc Indicates the time of message transmission, | 20190214-
dingTime p the consistency of the time provided is not 15:30:01.4
checked by the Exchange. 62743346
5979 | OEGINFromMemb | UTCTimestam 27 | Timestamp Cc Order Entry Gateway IN time from member | 29190214-
er p (in ns), measured when inbound message 15:28:52.8
enters the gateway 33883664
7764 | OEGOUTTOME UTCTimestam 27 | Timestamp Cc Gateway OUT time to ME (inns), measured | 29190214-
p when inbound message leaves the gateway | 15-28-52.8
34193232
21002 | BookINTime UTCTimestam 27 | Timestamp A Time of order creation in ME 20190214-
p 15:28:52.8
40530924
21003 | BookOUTTime UTCTimestam | 27 | Timestamp c Matching Engine OUT time (in ns), when 20190214-
p message leaves the Matching Engine (ME) 15:28:52.8
40568733
7765 | OEGINFromME UTCTimestam | 27 | Timestamp c Gateway IN time from ME (in ns), measured | 29190214-
p when outbound message enters the 15:28:52.8
gateway 33883664
11 CclOrdiD String 20 | From -2463 to 2463-1 A Identifier of an Order assigned by the Client | 39
when submitting an order to the Exchange
48 SecuritylD String 10 | From 0 to 2432-2 M Exchange defined ID of an 1110530
instrument/contract
22 SecurityIDSource String 1 8 = Symbol Index M Type of the SecurityID. Always set to 8 8
20020 | EMM Int 2 1 = Cash and Derivative Central Order Book (COB) A Exchange Market Mechanism a
7 = Derivative On Exchange Off book
8 = ETF MTF - NAV Central Order Book
37 OrderID String 20 | From 0 to 2464-2 M Numerical order identifier assigned by ME. 5
For acknowledgement of RFQ populated
with the same value as in field QuoteReqID
(131)
39 OrdStatus Char 1 0=New M Order status 0
        """

    example_1_assistant_message = """
[
  {
    "Tag": 21005,
    "Field Name": "ClientMessageSendingTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Indicates the time of message transmission, the consistency of the time provided is not checked by the Exchange.",
    "Value Example": "20190214-15:30:01.462743346"
  },
  {
    "Tag": 5979,
    "Field Name": "OEGINFromMember",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Order Entry Gateway IN time from member (in ns), measured when inbound message enters the gateway.",
    "Value Example": "29190214-15:28:52.833883664"
  },
  {
    "Tag": 7764,
    "Field Name": "OEGOUTTOME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Gateway OUT time to ME (in ns), measured when inbound message leaves the gateway.",
    "Value Example": "29190214-15-28-52.834193232"
  },
  {
    "Tag": 21002,
    "Field Name": "BookINTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Time of order creation in ME.",
    "Value Example": "20190214-15:28:52.840530924"
  },
  {
    "Tag": 21003,
    "Field Name": "BookOUTTime",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Matching Engine OUT time (in ns), when message leaves the Matching Engine (ME).",
    "Value Example": "20190214-15:28:52.840568733"
  },
  {
    "Tag": 7765,
    "Field Name": "OEGINFromME",
    "Format": "UTCTimestamp",
    "Len": 27,
    "Possible Values": "Timestamp",
    "M/C": "C",
    "Short Description, Compatibility Notes, Value & Conditions": "Gateway IN time from ME (in ns), measured when outbound message enters the gateway.",
    "Value Example": "29190214-15:28:52.833883664"
  },
  {
    "Tag": 11,
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From -2463 to 2463-1",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Identifier of an Order assigned by the Client when submitting an order to the Exchange.",
    "Value Example": "39"
  },
  {
    "Tag": 48,
    "Field Name": "SecurityID",
    "Format": "String",
    "Len": 10,
    "Possible Values": "From 0 to 2432-2",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Exchange defined ID of an instrument/contract.",
    "Value Example": "1110530"
  },
  {
    "Tag": 22,
    "Field Name": "SecurityIDSource",
    "Format": "String",
    "Len": 1,
    "Possible Values": "8 = Symbol Index",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Type of the SecurityID. Always set to 8.",
    "Value Example": "8"
  },
  {
    "Tag": 20020,
    "Field Name": "EMM",
    "Format": "Int",
    "Len": 2,
    "Possible Values": "1 = Cash and Derivative Central Order Book (COB), 7 = Derivative On Exchange Off book, 8 = ETF MTF - NAV Central Order Book",
    "M/C": "A",
    "Short Description, Compatibility Notes, Value & Conditions": "Exchange Market Mechanism.",
    "Value Example": ""
  },
  {
    "Tag": 37,
    "Field Name": "OrderID",
    "Format": "String",
    "Len": 20,
    "Possible Values": "From 0 to 2464-2",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Numerical order identifier assigned by ME. For acknowledgement of RFQ populated with the same value as in field QuoteReqID (131).",
    "Value Example": "5"
  },
  {
    "Tag": 39,
    "Field Name": "OrdStatus",
    "Format": "Char",
    "Len": 1,
    "Possible Values": "0=New",
    "M/C": "M",
    "Short Description, Compatibility Notes, Value & Conditions": "Order status.",
    "Value Example": "0"
  }
]
        """

    example_2_human_message = """
Tag Field Name
Standard Header
35 MsgType
Message Body
268 NoMDEntries
>
>
279
269
278
48
22
454
MDUpdateAction
MDEntryType
MDEntryID
Securityld
SecurityIDsource
NoSecurityAltID
Req Description
X = Market Data Incremental Refresh
Number of entries following.
Type of Market Data update action.
Value Meaning
0 New
1 Update
2 Delete
Types of Market Data Entries that the firm requesting
the Market Data is interested in receiving.
Value Meaning
0 Bid
1 Offer
Unique entry identifier.
Will be same as the OrderlD value for a firm order or
an indicative quote side.
The CUSIP or the ISIN of the symbol.
Source database of the Security Id for a given
symbol.
By default this field will be populated with the ISIN.
If ISIN is NOT present this will contain the CUSIP of
the instrument.
Value Meaning
1 CUSIP
4 ISIN
Number of alternate Security Identifiers

=> 455 SecurityAltID N
=> 456 SecurityAltIDSource N
+ 270 MDEntryPx N
+ 271 MDEntrySize N
+ 1023 MDPriceLevel Y
+ 290 MDEntryPositionNo Y
+ 6373 FirmnessIndicator N
> 110 MinQty N
+ 6372 Mine N
MMI BondsPro — FIX 4.4 Market Data Feed
Security Alternate identifier for this security
Source of SecurityAItID <455>. Required if
SecurityAltID <455> is specified.
Value Meaning
1 CUSIP
Used if the entry has price related data. Unmarked
flat price will be populated always.
Required only if the MDUpdateAction(279) is 'New(0)'
or 'Update(1)’.
Quantity or volume represented by the Market Data
Entry.
Required only if the MDUpdateAction(279) is 'New(0)'
or 'Update(1)’.
Integer to convey the level of a bid or offer at a given
price level.
This is in contrast to MDEntryPositionNo which is
used to convey the position of an order within a Price
level.
Display position of a bid or offer within a price level,
numbered from most competitive to least
competitive, beginning with 1.
Indicates the quality of market data for indicative
quotes (>0).
A Firmness Indicator value of 0 is reserved to
represent firm orders.
Value Meaning
0 Firm Order
>0 Subject quote and quality of market data
Permission
1. Population of the tag is dependent on
the required permissions being
present for the user who is receiving
market data
Minimum quantity of the order in Buy or Sell side. By
default the value for this field will be set to 0.
Indicates whether the interest was submitted by the
same firm or an external firm.
        """

    example_2_assistant_message = """
[
  {
    "Tag": 35,
    "Field Name": "MsgType",
    "Req Description": "X = Market Data Incremental Refresh"
  },
  {
    "Tag": 268,
    "Field Name": "NoMDEntries",
    "Req Description": "Number of entries following."
  },
  {
    "Tag": 279,
    "Field Name": "MDUpdateAction",
    "Req Description": "Type of Market Data update action.",
    "Value Meaning": {
      "0": "New",
      "1": "Update",
      "2": "Delete"
    }
  },
  {
    "Tag": 269,
    "Field Name": "MDEntryType",
    "Req Description": "Types of Market Data Entries that the firm requesting the Market Data is interested in receiving.",
    "Value Meaning": {
      "0": "Bid",
      "1": "Offer"
    }
  },
  {
    "Tag": 278,
    "Field Name": "MDEntryID",
    "Req Description": "Unique entry identifier. Will be same as the OrderID value for a firm order or an indicative quote side."
  },
  {
    "Tag": 48,
    "Field Name": "SecurityID",
    "Req Description": "The CUSIP or the ISIN of the symbol."
  },
  {
    "Tag": 22,
    "Field Name": "SecurityIDSource",
    "Req Description": "Source database of the Security Id for a given symbol. By default this field will be populated with the ISIN. If ISIN is NOT present this will contain the CUSIP of the instrument.",
    "Value Meaning": {
      "1": "CUSIP",
      "4": "ISIN"
    }
  },
  {
    "Tag": 454,
    "Field Name": "NoSecurityAltID",
    "Req Description": "Number of alternate Security Identifiers"
  },
  {
    "Tag": 455,
    "Field Name": "SecurityAltID",
    "Req Description": "Security Alternate identifier for this security"
  },
  {
    "Tag": 456,
    "Field Name": "SecurityAltIDSource",
    "Req Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
    "Value Meaning": {
      "1": "CUSIP"
    }
  },
  {
    "Tag": 270,
    "Field Name": "MDEntryPx",
    "Req Description": "Used if the entry has price related data. Unmarked flat price will be populated always. Required only if the MDUpdateAction(279) is \'New(0)\'
or \'Update(1)\'."
  },
  {
    "Tag": 271,
    "Field Name": "MDEntrySize",
    "Req Description": "Quantity or volume represented by the Market Data Entry. Required only if the MDUpdateAction(279) is \'New(0)\' or \'Update(1)\'."
  },
  {
    "Tag": 1023,
    "Field Name": "MDPriceLevel",
    "Req Description": "Integer to convey the level of a bid or offer at a given price level. This is in contrast to MDEntryPositionNo which is used to convey the position of an order within a Price level."
  },
  {
    "Tag": 290,
    "Field Name": "MDEntryPositionNo",
    "Req Description": "Display position of a bid or offer within a price level, numbered from most competitive to least competitive, beginning with 1."
  },
  {
    "Tag": 6373,
    "Field Name": "FirmnessIndicator",
    "Req Description": "Indicates the quality of market data for indicative quotes (>0). A Firmness Indicator value of 0 is reserved to represent firm orders.",
    "Value Meaning": {
      "0": "Firm Order",
      ">0": "Subject quote and quality of market data"
    },
    "Permission": "1. Population of the tag is dependent on the required permissions being present for the user who is receiving market data"
  },
  {
    "Tag": 110,
    "Field Name": "MinQty",
    "Req Description": "Minimum quantity of the order in Buy or Sell side. By default the value for this field will be set to 0."
  },
  {
    "Tag": 6372,
    "Field Name": "Mine",
    "Req Description": "Indicates whether the interest was submitted by the same firm or an external firm."
  }
]
        """

    example_3_human_message = """
FIX tag | Field Name R| Field | Description
e | Form
q| at
d
35 MsgType Y | See Message Type.
8.16 CO = SecurityMassStatus
34 See an
MsgSeqNum x 815 The sequence number of the message is incremented p
, maintenance feed message.
See
49 SenderCompld ¥ 8.28 Source ID of sender
1679 SecurityMassTradingStatus Y| See 2: Trading Halt
8.25 17: Ready to Trade
18: Not available for trading
23: Fast Market
1680 SecurityMassTradingEvent Y| See 2: Market Reset, Trading resumes.
8.24 5: Change of Trading Subsession; Exchange segment
state change.
6: Change of SecurityTradingStatus; Fast Market chang
1544 InstrumentScopeProductComplex | N| See This tag is restricted to instruments in trading model
8.2 “Continuous Auction” only. The target state is always
delivered with TradingSessionSubID (625). Mutually
exclusive with (1616, 1547) and 1545.
        """

    example_3_assistant_message = """
[
  {
    "FIX tag": 35,
    "Field Name": "MsgType",
    "Required": "Y",
    "Field Format": "See Message Type.",
    "Field Description": "CO = SecurityMassStatus"
  },
  {
    "FIX tag": 34,
    "Field Name": "MsgSeqNum",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "The sequence number of the message is incremented, maintenance feed message."
  },
  {
    "FIX tag": 49,
    "Field Name": "SenderCompID",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "Source ID of sender"
  },
  {
    "FIX tag": 1679,
    "Field Name": "SecurityMassTradingStatus",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "2: Trading Halt, 17: Ready to Trade, 18: Not available for trading, 23: Fast Market"
  },
  {
    "FIX tag": 1680,
    "Field Name": "SecurityMassTradingEvent",
    "Required": "Y",
    "Field Format": "See",
    "Field Description": "2: Market Reset, Trading resumes, 5: Change of Trading Subsession; Exchange segment state change, 6: Change of SecurityTradingStatus; Fast Market change"
  },
  {
    "FIX tag": 1544,
    "Field Name": "InstrumentScopeProductComplex",
    "Required": "N",
    "Field Format": "See",
    "Field Description": "This tag is restricted to instruments in trading model “Continuous Auction” only. The target state is always delivered with TradingSessionSubID (625). Mutually exclusive with (1616, 1547) and 1545."
  }
]
        """

    human_message = """
    ### INPUT ###
        """

    for text_table in text_tables:
        human_message += f"{text_table} "

    human_message += """
    ### OUTPUT JSON ###
        """

    # ai_model = ChatOpenAI(
    #     openai_api_key=utils.openai_api_key,
    #     model=utils.ai_model_name,
    #     temperature=0,
    #     top_p=0
    # )
    #
    # json_array_document_fields = ai_model([
    #     SystemMessage(content=utils.replace_newlines_with_space(system_message)),
    #     HumanMessage(content=example_1_human_message),
    #     AIMessage(content=example_1_assistant_message),
    #     HumanMessage(content=example_2_human_message),
    #     AIMessage(content=example_2_assistant_message),
    #     HumanMessage(content=example_3_human_message),
    #     AIMessage(content=example_3_assistant_message),
    #     HumanMessage(content=utils.replace_newlines_with_space(human_message))
    # ])

    # return json.loads(json_array_document_fields.content)

    with open('document_fields.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_message_components(json_array_document_fields_pages):
    json_array_repeating_groups = []

    for i in range(len(json_array_document_fields_pages) - 1):
        current_json_array_document_fields_page = json_array_document_fields_pages[i]
        next_json_array_document_fields_page = json_array_document_fields_pages[i + 1]
        json_array_document_fields_of_adjacent_pages = current_json_array_document_fields_page + next_json_array_document_fields_page
        print(f"- {i} {i + 1} #")

        partial_json_array_repeating_groups = generate_repeating_groups(json_array_document_fields_of_adjacent_pages)

        for repeating_group in partial_json_array_repeating_groups:
            if repeating_group["group_id"] not in json_array_repeating_groups:
                json_array_repeating_groups.append(repeating_group)

    json_array_sbe_fields = []

    for json_array_document_fields_page in json_array_document_fields_pages:
        partial_json_array_sbe_fields = generate_sbe_fields(json_array_document_fields_page)
        json_array_sbe_fields.extend(partial_json_array_sbe_fields)

    for repeating_group in json_array_repeating_groups:
        repeating_group["items"] = generate_sbe_fields(repeating_group["items"])
        with open('sbe_fields_repeating_group.json', 'r') as file:
            file_content = file.read()
            repeating_group["items"] = json.loads(file_content)

    ids_to_remove = set()
    names_to_remove = set()

    for repeating_group in json_array_repeating_groups:
        for group_sbe_field in repeating_group["items"]:
            ids_to_remove.add(group_sbe_field["field_id"])
            names_to_remove.add(group_sbe_field["field_name"])

    filtered_sbe_fields = []

    for field in json_array_sbe_fields:
        if field["field_id"] not in ids_to_remove and field["field_name"] not in names_to_remove:
            filtered_sbe_fields.append(field)

    return {
        "json_array_sbe_fields": filtered_sbe_fields,
        "json_array_repeating_groups": json_array_repeating_groups
    }


def generate_repeating_groups(array_document_fields):
    system_message = """
Sei esperto in sistemi di trading elettronico e conosci approfonditamente i protocolli FIX e SBE. Devi analizzare un array JSON contenente informazioni sui campi di un messaggio SBE per identificare se alcuni di essi formano un repeating group, basandoti su criteri specifici:
- Pattern nei Nomi: Campi con nomi simili, come PartyIDGroup, PartyIDSource, PartyIDRole, PartyIDRoleQualifier, indicano un insieme comune.
- Sequenza Numerica: I campi di un repeating group sono tipicamente in sequenza numerica continua o raggruppati senza interruzioni.
- Descrizione dei Campi: Termini come "party" o "group" nelle descrizioni possono suggerire l'appartenenza a un repeating group.
- Consistenza nei Tipi di Dato e Lunghezza: I campi in un repeating group solitamente hanno tipi di dato simili e un campo che indica la lunghezza o il numero di elementi spesso precede il gruppo.
- Correlazione Semantica: Una logica relazione tra i campi può indicare che rappresentano attributi di un medesimo oggetto o concetto.
- Indicatori di Inizio/Fine: In alcuni casi, i repeating groups sono delimitati da campi speciali che segnano l'inizio e la fine o presentano un campo composito come intestazione.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun gruppo ripetuto, un oggetto JSON che lo descrive con i rispettivi campi. Ogni oggetto JSON deve contenere:
- group_id: l'identificativo del campo che indica il numero di elementi nel gruppo (NumInGroup),
- group_name: un nome proposto per il gruppo, derivato dai nomi dei campi,
- items: un array JSON contenente un oggetto per ogni campo all'interno del gruppo ripetuto, includendo tutte le informazioni disponibili.

Qualora non siano presenti gruppi ripetuti, l'output sarà un array JSON vuoto.

Segui gli esempi che ti sono stati forniti.
    """

    example_1_human_message = """
[
  {
    "Tag": "21038",
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY"
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY"
  },
  {
    "Tag": "453",
    "Field Name": "NoPartyIDs",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "Always set to 1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Number of PartyID entries",
    "Value Example": "1"
  },
  {
    "Tag": "448",
    "Field Name": "PartyID",
    "Format": "String",
    "Len": "11",
    "Possible Values": "Alphanumeric",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "In this case provides the ExecutionWithinFirmShortCode",
    "Value Example": "59786"
  },
  {
    "Tag": "447",
    "Field Name": "PartyIDSource",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "P = Short code identifier",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Source of PartyID value",
    "Value Example": "P"
  },
  {
    "Tag": "452",
    "Field Name": "PartyRole",
    "Format": "Int",
    "Len": "3",
    "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifies the type or role of the PartyID specified.",
    "Value Example": "3"
  },
  {
    "Tag": "2376",
    "Field Name": "PartyRoleQualifier",
    "Format": "Int",
    "Len": "2",
    "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used to further qualify the value of PartyRole",
    "Value Example": "23"
  },
  {
    "Tag": "1724",
    "Field Name": "OrderOrigination",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "5 = Order received from a direct access or sponsored access customer",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Identifies the origin of the order",
    "Value Example": ""
  },
  {
    "Tag": "2593",
    "Field Name": "NoOrderAttributes",
    "Format": "NumInGroup",
    "Len": "1",
    "Possible Values": "If provided, from 1 to 2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Number of order attribute entries",
    "Value Example": ""
  },
  {
    "Tag": "2594",
    "Field Name": "OrderAttributeType",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, OR in Risk Reduction order",
    "Value Example": ""
  },
  {
    "Tag": "2595",
    "Field Name": "OrderAttributeValue",
    "Format": "String",
    "Len": "1",
    "Possible Values": "Y = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Always set to Yes if OrderAttributeType if provided",
    "Value Example": ""
  }
]
    """

    example_1_assistant_message = """
[
  {
    "group_id": "453",
    "group_name": "PartyIDGroup",
    "items": [
      {
        "Tag": "448",
        "Field Name": "PartyID",
        "Format": "String",
        "Len": "11",
        "Possible Values": "Alphanumeric",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "In this case provides the ExecutionWithinFirmShortCode",
        "Value Example": "59786"
      },
      {
        "Tag": "447",
        "Field Name": "PartyIDSource",
        "Format": "Char",
        "Len": "1",
        "Possible Values": "P = Short code identifier",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "Source of PartyID value",
        "Value Example": "P"
      },
      {
        "Tag": "452",
        "Field Name": "PartyRole",
        "Format": "Int",
        "Len": "3",
        "Possible Values": "3 = Client ID, 12 = Executing Trader, 999 = Not Applicable",
        "M/C": "A",
        "Short Description, Compatibility Notes & Conditions": "Identifies the type or role of the PartyID specified.",
        "Value Example": "3"
      },
      {
        "Tag": "2376",
        "Field Name": "PartyRoleQualifier",
        "Format": "Int",
        "Len": "2",
        "Possible Values": "22 = Algorithm, 23 = Firm or legal entity, 24 = Natural person, 99 = Not Applicable",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Used to further qualify the value of PartyRole",
        "Value Example": "23"
      }
    ]
  },
  {
    "group_id": "2593",
    "group_name": "OrderAttributesGroup",
    "items": [
      {
        "Tag": "2594",
        "Field Name": "OrderAttributeType",
        "Format": "Int",
        "Len": "1",
        "Possible Values": "0 = Aggregated order, 1 = Pending allocation, 3 = Risk reduction order",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Used in case client needs to indicate values of AGGR or PNAL, OR in Risk Reduction order",
        "Value Example": ""
      },
      {
        "Tag": "2595",
        "Field Name": "OrderAttributeValue",
        "Format": "String",
        "Len": "1",
        "Possible Values": "Y = Yes",
        "M/C": "C",
        "Short Description, Compatibility Notes & Conditions": "Always set to Yes if OrderAttributeType if provided",
        "Value Example": ""
      }
    ]
  }
]
    """

    example_2_human_message = """
[
  {
    "Tag": "454",
    "FieldName": "NoSecurityAltID",
    "Req": "N",
    "Description": "Number of alternate Security Identifiers"
  },
  {
    "Tag": "455",
    "FieldName": "SecurityAltID",
    "Req": "N",
    "Description": "Security Alternate identifier for this security"
  },
  {
    "Tag": "456",
    "FieldName": "SecurityAltIDSource",
    "Req": "N",
    "Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
    "Value Meaning": {
      "1": "CUSIP"
    }
  },
  {
    "Tag": "326",
    "FieldName": "SecurityTradingStatus",
    "Req": "Y",
    "Description": "Indicates the current trading session for the instrument.",
    "Value Meaning": {
      "2": "Halt",
      "3": "Resume",
      "111": "Pause",
      "112": "End of Pause"
    }
  },
  {
    "Tag": "1174",
    "FieldName": "SecurityTradingEvent",
    "Req": "N",
    "Description": "Indicates the reason a trading session is extended or shortened.",
    "Value Meaning": {
      "101": "Extended by Market Operations",
      "102": "Shortened by Market Operations"
    }
  }
]
    """

    example_2_assistant_message = """
[
  {
    "group_id": "454",
    "group_name": "SecurityAltIDGroup",
    "items": [
      {
        "Tag": "455",
        "FieldName": "SecurityAltID",
        "Req": "N",
        "Description": "Security Alternate identifier for this security"
      },
      {
        "Tag": "456",
        "FieldName": "SecurityAltIDSource",
        "Req": "N",
        "Description": "Source of SecurityAltID <455>. Required if SecurityAltID <455> is specified.",
        "Value Meaning": {
          "1": "CUSIP"
        }
      }
    ]
  }
]
    """

    example_3_human_message = """
[
  {
    "FIX tag": "35",
    "Field Name": "MsgType",
    "Req’d": "Y",
    "Field Format": "See 8.16",
    "Description": "X = MarketDataIncrementalRefresh"
  },
  {
    "FIX tag": "34",
    "Field Name": "MsgSeqNum",
    "Req’d": "Y",
    "Field Format": "See 8.15",
    "Description": "The sequence number of the message is incremented per ticker message."
  },
  {
    "FIX tag": "49",
    "Field Name": "SenderCompID",
    "Req’d": "Y",
    "Field Format": "See 8.28",
    "Description": "Source ID of sender"
  },
  {
    "FIX tag": "268",
    "Field Name": "NoMDEntries",
    "Req’d": "Y",
    "Field Format": "See 8.17",
    "Description": "Defines the size of the repeating group"
  },
  {
    "FIX tag": "279",
    "Field Name": "MDUpdateAction",
    "Req’d": "Y",
    "Field Format": "See 8.14",
    "Description": "0= New ; always “new”"
  },
  {
    "FIX tag": "48",
    "Field Name": "SecurityID",
    "Req’d": "Y",
    "Field Format": "See 8.23",
    "Description": "ISIN of instrument"
  },
  {
    "FIX tag": "270",
    "Field Name": "MDEntryPx",
    "Req’d": "Y",
    "Field Format": "See 8.8",
    "Description": "Price or index value"
  },
  {
    "FIX tag": "271",
    "Field Name": "MDEntrySize",
    "Req’d": "N",
    "Field Format": "See 8.9",
    "Description": "Quantity, not set for indices"
  },
  {
    "FIX tag": "273",
    "Field Name": "MDEntryTime",
    "Req’d": "N",
    "Field Format": "See 8.10",
    "Description": "Time of market data entry"
  },
  {
    "FIX tag": "15",
    "Field Name": "Currency",
    "Req’d": "N",
    "Field Format": "See 8.1",
    "Description": "Price currency"
  },
  {
    "FIX tag": "1500",
    "Field Name": "MDStreamID",
    "Req’d": "Y",
    "Field Format": "See 8.13",
    "Description": "Name of the price source"
  }
]
    """

    example_3_assistant_message = """
[
  {
    "group_id": "268",
    "group_name": "MDEntriesGroup",
    "items": [
      {
        "FIX tag": "279",
        "Field Name": "MDUpdateAction",
        "Req’d": "Y",
        "Field Format": "See 8.14",
        "Description": "0= New ; always “new”"
      },
      {
        "FIX tag": "48",
        "Field Name": "SecurityID",
        "Req’d": "Y",
        "Field Format": "See 8.23",
        "Description": "ISIN of instrument"
      },
      {
        "FIX tag": "270",
        "Field Name": "MDEntryPx",
        "Req’d": "Y",
        "Field Format": "See 8.8",
        "Description": "Price or index value"
      },
      {
        "FIX tag": "271",
        "Field Name": "MDEntrySize",
        "Req’d": "N",
        "Field Format": "See 8.9",
        "Description": "Quantity, not set for indices"
      },
      {
        "FIX tag": "273",
        "Field Name": "MDEntryTime",
        "Req’d": "N",
        "Field Format": "See 8.10",
        "Description": "Time of market data entry"
      },
      {
        "FIX tag": "15",
        "Field Name": "Currency",
        "Req’d": "N",
        "Field Format": "See 8.1",
        "Description": "Price currency"
      },
      {
        "FIX tag": "1500",
        "Field Name": "MDStreamID",
        "Req’d": "Y",
        "Field Format": "See 8.13",
        "Description": "Name of the price source"
      }
    ]
  }
]
    """

    example_4_human_message = """
[
  {
    "Tag": "20175",
    "Field Name": "TriggeredStopTimeInForce",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "0 = Day, 1 = Good Till Cancel, 6 = Good till Date",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Specifies the maximum validity of an triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59).",
    "Value Example": "CASH ONLY - Specifies the maximum validity of an triggered stop order. On triggering of a Stop order the value in this field is populated in the field TimeInForce (59)."
  },
  {
    "Tag": "131",
    "Field Name": "QuoteReqID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From 0 to 2^64-2",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM.",
    "Value Example": "CASH ONLY - Numerical RFQ identifier assigned by the matching engine, unique per instrument and EMM."
  },
  {
    "Tag": "21037",
    "Field Name": "RFQAnswerIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, a quote sent as an answer to a QuoteRequest (R) message."
  },
  {
    "Tag": "21038",
    "Field Name": "RFQConfirmationIndicator",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = No, 1 = Yes",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message.",
    "Value Example": "CASH ONLY - Indicates whether the message is, or not, an order sent as a confirmation of a QuoteRequest (R) message."
  },
  {
    "Tag": "21800",
    "Field Name": "ConditionalOrderFlag",
    "Format": "Int",
    "Len": "1",
    "Possible Values": "0 = Firm (default), 1 = Conditional",
    "M/C": "C",
    "Short Description, Compatibility Notes & Conditions": "Indicates if the order is a conditional or a firm order",
    "Value Example": "CASH ONLY - Indicates if the order is a conditional or a firm order"
  }
]
    """

    example_4_assistant_message = """
[]
    """

    human_message = """
### INPUT DELLO SVILUPPATORE ###
    """

    for document_field in array_document_fields:
        human_message += f"{document_field} "

    human_message += """
### OUTPUT JSON ###
    """

    # ai_model = ChatOpenAI(
    #     openai_api_key=utils.openai_api_key,
    #     model=utils.ai_model_name,
    #     temperature=0,
    #     top_p=0
    # )
    #
    # json_array_repeating_groups = ai_model([
    #     SystemMessage(content=utils.replace_newlines_with_space(system_message)),
    #     HumanMessage(content=example_1_human_message),
    #     AIMessage(content=example_1_assistant_message),
    #     HumanMessage(content=example_2_human_message),
    #     AIMessage(content=example_2_assistant_message),
    #     HumanMessage(content=example_3_human_message),
    #     AIMessage(content=example_3_assistant_message),
    #     HumanMessage(content=example_4_human_message),
    #     AIMessage(content=example_4_assistant_message),
    #     HumanMessage(content=human_message
    # )
    # ])
    # return json.loads(json_array_repeating_groups.content)
    with open('repeating_groups.json', 'r') as file:
        data = json.load(file)

    return data


def generate_sbe_fields(array_document_fields):
    system_message = """
Sei un esperto in sistemi di trading elettronico con una profonda conoscenza dei protocolli FIX e SBE. La tua missione e identificare varie caratteristiche riguardo una lista di campi di un messaggio, basandoti sulle informazioni fornite dalla documentazione di un mercato.

Ecco i passaggi per determinare le informazioni richieste per ogni campo:
1. ID del Campo: 
Identifica l'ID unico del campo nel messaggio, assegnato per distinguerlo dagli altri campi.
2. Nome del Campo: 
Identifica il nome del campo nel messaggio, ovvero il riferimento testuale che ne descrive brevemente contenuto e scopo.
3. Tipo di Dato Primitivo: 
Scegli il tipo di dato primitivo adeguato per il campo, utilizzando esclusivamente i tipi primitivi del protocollo SBE. Ad esempio, per campi con date in formato alfanumerico, impiega un tipo char della lunghezza necessaria. Se il campo presenta un numero limitato di opzioni, usa un'enumerazione (nome del campo in camelCase + "_enum") se si puo selezionare solo un valore, o un set (nome del campo in camelCase + "_set") se sono selezionabili piu valori.
4. Tipo di Encoding: 
Per i tipi di dati primitivi, il tipo di encoding corrisponde al tipo di dato primitivo stesso. Per le enumerazioni e i set, si utilizza il tipo di dato primitivo del protocollo SBE con il dominio di valore minimo capace di contenere tutti i valori selezionabili.
5. Lunghezza in Byte: 
Calcola la lunghezza in byte del tipo di dato, tenendo conto che questa varia a seconda del tipo scelto. Ad esempio, un char occupa generalmente 1 byte. Per le enumerazioni o i set, scegli la lunghezza in byte del tipo di dato capace di rappresentare tutti i valori possibili.
6. Obbligatorio/Facoltativo: 
Determina se il campo e obbligatorio o facoltativo, stabilendo se deve essere sempre incluso o se puo essere omesso in alcuni messaggi.
7. Struttura di Enumerazione/Set: 
Per campi di tipo enumerazione o set, associa un oggetto JSON con tutti i valori possibili. Se il tipo di dato e primitivo, usa un JSON vuoto {}.

Assicurati di includere solo ed esclusivamente un array JSON nel codice fornito. Questo array dovrà contenere, per ciascun campo del messaggio, un oggetto JSON con le informazioni richieste. Segui gli esempi che ti sono stati forniti.
    """

    example_1_human_message = """
[
  {
	"tag": "21005",
	"field name": "ClientMessageSen dingTime",
	"format": "uTCTimestam p",
	"len": "27",
	"possible values": "Timestamp",
	"m/c": "c",
	"short description, compatibility notes and conditions": "indicates the time of message transmission,  the consistency of the time provided is not  checked by the Exchange",
	"value example": "20190214- 15:30:01.4 62743346"
  },
  {
    "Tag": "11",
    "Field Name": "ClOrdID",
    "Format": "String",
    "Len": "20",
    "Possible Values": "From -2^63 to 2^63-1",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Identifier of an Order Modification message assigned by the Client when submitting the order modification message to the Exchange",
    "Value Example": "25"
  },
  {
    "Tag": "21013",
    "Field Name": "AckPhase",
    "Format": "Char",
    "Len": "1",
    "Possible Values": "1 = Continuous Trading Phase 2 = Call Phase 3 = Halt Phase 5 = Trading At Last Phase 6 = Reserved 7 = Suspended 8 = Random Uncrossing Phase",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Indicates the trading phase during which the Matching Engine has received the order Values 5 and 8 apply only for Cash markets",
    "Value Example": "1"
  },
  {
    "Tag": "21014",
    "Field Name": "AckQualifiers",
    "Format": "MultipleCharValue",
    "Len": "15",
    "Possible Values": "0 = Dark Indicator 1 = Queue Indicator 2 = Request with Client Order ID 3 = Use of Cross Partition 4 = Internal1 5 = Internal2 6 = Execution Upon Entry flag Enabled 7 = Executed Upon Entry flag",
    "M/C": "A",
    "Short Description, Compatibility Notes & Conditions": "Field used to provide additional information on the corresponding order. For Derivatives positions 0 is not applicable and is always set to 0.",
    "Value Example": "0 0 0 0 0 0 0 0"
  }
]
    """

    example_1_assistant_message = """
[
  {
    "field_id": 21005,
    "field_name": "ClientMessageSendingTime",
    "data_type": "char",
    "encoding_type": "char",
    "length": 27,
    "presence": "optional",
    "structure": {}
  },
  {
    "field_id": 11,
    "field_name": "ClOrdID",
    "data_type": "int64",
    "encoding_type": "int64",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 21013,
    "field_name": "AckPhase",
    "data_type": "ackPhase_enum",
    "encoding_type": "char",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "1": "Continuous Trading Phase",
      "2": "Call Phase",
      "3": "Halt Phase",
      "5": "Trading At Last Phase",
      "6": "Reserved",
      "7": "Suspended",
      "8": "Random Uncrossing Phase"
    }
  },
  {
    "field_id": 21014,
    "field_name": "AckQualifiers",
    "data_type": "ackQualifiers_set",
    "encoding_type": "char",
    "length": 15,
    "presence": "mandatory",
    "structure": {
      "0": "Dark Indicator",
      "1": "Queue Indicator",
      "2": "Request with Client Order ID",
      "3": "Use of Cross Partition",
      "4": "Internal1",
      "5": "Internal2",
      "6": "Execution Upon Entry flag Enabled",
      "7": "Executed Upon Entry flag"
    }
  }
]
    """

    example_2_human_message = """
[
  {
    "Offset": "0",
    "Field": "MsgSize",
    "Format": "Uint16",
    "Len": "2",
    "Description": "Size of the message",
    "Values": "N/A"
  },
  {
    "Offset": "8",
    "Field": "SecurityTradingStatus",
    "Format": "Uint8",
    "Len": "1",
    "Description": "Identifies the trading status of a security.",
    "Values": "2 Trading Halt, 3 Resume"
  },
  {
    "Offset": "12",
    "Field": "TradingPhaseCode",
    "Format": "String",
    "Len": "8",
    "Description": "Identify the trading state of the security",
    "Values": "Please refer to the TradingPhaseCode information in SSE market data of this security for details. N/A for SZSE Instruments"
  }
]
    """

    example_2_assistant_message = """
[
  {
    "field_id": 0,
    "field_name": "MsgSize",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 8,
    "field_name": "SecurityTradingStatus",
    "data_type": "SecurityTradingStatus_enum",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "2": "Trading Halt",
      "3": "Resume"
    }
  },
  {
    "field_id": 12,
    "field_name": "TradingPhaseCode",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  }
]
    """

    example_3_human_message = """
[
  {
    "Field": "SEDOL",
    "Offset": "31",
    "Length": "8",
    "Type": "Alpha",
    "Description": "SEDOL code of the instrument."
  },
  {
    "Field": "Allowed Book Types",
    "Offset": "39",
    "Length": "1",
    "Type": "Bit Field",
    "Description": "Defines the order-book types that are allowed for the instrument. Each designated bit represents a book type. 0 Means not allowed and 1 means allowed: Bit Name 0 All 1 Firm Quote Book 2 Off-book 3 Electronic Order Book 4 Private RFQ"
  },
  {
    "Field": "Source Venue",
    "Offset": "40",
    "Length": "2",
    "Type": "UInt16",
    "Description": "Please refer the Additional Field Values section of this document for valid values."
  },
  {
    "Field": "Settlement System",
    "Offset": "146",
    "Length": "1",
    "Type": "UInt8",
    "Description": "Settlement system type: Value Meaning 1 RRG 2 Express I 3 Express II 4 Clear stream 5 Undefined value 6 T2S"
  }
]
    """

    example_3_assistant_message = """
[
  {
    "field_id": 31,
    "field_name": "SEDOL",
    "data_type": "char",
    "encoding_type": "char",
    "length": 8,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 39,
    "field_name": "AllowedBookTypes",
    "data_type": "allowedBookTypes_set",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "0": "All",
      "1": "Firm Quote Book",
      "2": "Off-book",
      "3": "Electronic Order Book",
      "4": "Private RFQ"
    }
  },
  {
    "field_id": 40,
    "field_name": "SourceVenue",
    "data_type": "uint16",
    "encoding_type": "uint16",
    "length": 2,
    "presence": "mandatory",
    "structure": {}
  },
  {
    "field_id": 146,
    "field_name": "SettlementSystem",
    "data_type": "settlementSystem_enum",
    "encoding_type": "uint8",
    "length": 1,
    "presence": "mandatory",
    "structure": {
      "1": "RRG",
      "2": "Express I",
      "3": "Express II",
      "4": "Clearstream",
      "5": "Undefined value",
      "6": "T2S"
    }
  }
]
    """

    human_message = """
### INPUT ###
        """

    for document_field in array_document_fields:
        human_message += f"{document_field} "

    human_message += """
### OUTPUT JSON ###
        """

    # ai_model = ChatOpenAI(
    #     openai_api_key=utils.openai_api_key,
    #     model=utils.ai_model_name,
    #     temperature=0,
    #     top_p=0
    # )
    #
    # json_array_sbe_fields = ai_model([
    #     SystemMessage(content=utils.replace_newlines_with_space(system_message)),
    #     HumanMessage(content=example_1_human_message),
    #     AIMessage(content=example_1_assistant_message),
    #     HumanMessage(content=example_2_human_message),
    #     AIMessage(content=example_2_assistant_message),
    #     HumanMessage(content=example_3_human_message),
    #     AIMessage(content=example_3_assistant_message),
    #     HumanMessage(content=human_message)
    # ])
    #
    # return json.loads(json_array_sbe_fields.content)
    with open('sbe_fields.json', 'r') as file:
        data = json.load(file)

    return data


def execute_pipeline(file_name, folder_path, pipeline_functions):

    image_path = os.path.join(folder_path, file_name)
    data = image_path
    logger.info(f"current image path: {image_path}")

    i = 1
    for function in pipeline_functions:
        try:
            data = function(data)
            logger.info(f"num filter: {i}")
            i = i + 1
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Errore nel processare l'immagine {file_name}: {e}")

    return data


def process(pdf_path, starting_page, ending_page, folder_path="extracted_pdf_pages"):

    convert_pdf_pages_to_jpg(pdf_path, starting_page, ending_page, folder_path)

    array_file_names = [file for file in os.listdir(folder_path) if file.endswith(('.jpg', '.jpeg', '.png'))]

    pipeline_functions = [
        convert_grayscale,
        increase_contrast,
        thresholding,
        detect_tables,
        ocr_tables,
        generate_document_fields
    ]

    multi_cpu = multiprocessing.cpu_count()
    single_cpu = 1
    pool = multiprocessing.Pool(processes=single_cpu)
    logger.info(f"number of cpu: {multiprocessing.cpu_count()}")

    process_partial = partial(execute_pipeline, folder_path=folder_path, pipeline_functions=pipeline_functions)
    array_document_fields_pages = pool.map(process_partial, array_file_names)

    sbe_message_components = generate_sbe_message_components(array_document_fields_pages)

    json_array_sbe_fields = sbe_message_components["json_array_sbe_fields"]
    json_array_repeating_groups = sbe_message_components["json_array_repeating_groups"]

    with open('deprecated/proof_data.txt', 'a', encoding="utf-8") as file:
        file.write("array_sbe_fields:\n")
        for data in json_array_sbe_fields:
            file.write(f"{data}\n")
        file.write("array_repeating_groups:\n")
        for data in json_array_repeating_groups:
            file.write(f"{data}\n")

    return json_array_sbe_fields, json_array_repeating_groups


if __name__ == "__main__":
    process("pdf_documents/drop_copy_service.pdf", 23, 35, "extracted_pdf_pages")
