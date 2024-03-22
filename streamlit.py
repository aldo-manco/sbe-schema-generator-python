# app.py

import streamlit as st
import json

from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from json_schema_handler import JsonSchemaHandler
from xml_sbe_schema_handler import XmlSbeSchemaHandler

tab_new_json_schema = "Add New JSON Schema File"
tab_new_document_message = "Add New Document Message"
tab_new_document_message_column = "Add New Document Message Column"
tab_new_document_message_field = "Add New Document Message Field"
tab_new_document_repeating_group = "Add New Document Repeating Group"
tab_new_document_composite = "Add New Document Composite"
tab_generate_sbe_xml_schema = "Generate SBE XML Schema"

ai_model_name = "gpt-4-0125-preview"
openai_api_key = ""


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
        openai_api_key=openai_api_key,
        model=ai_model_name,
        temperature=0,
        top_p=0
    )

    formatted_report_text = ai_model([
        SystemMessage(content=system_message),
        HumanMessage(content=example_1_human_message),
        AIMessage(content=example_1_assistant_message),
        HumanMessage(content=example_2_human_message),
        AIMessage(content=example_2_assistant_message),
        HumanMessage(content=example_3_human_message),
        AIMessage(content=example_3_assistant_message),
        HumanMessage(content=human_message)
    ])

    return replace_newlines_with_space(formatted_report_text.content)


def replace_newlines_with_space(input_string):
    return input_string.replace('\n', ' ')


def generate_sbe_data_type_definitions(json_handler, sbe_field):
    if sbe_field["data_type"].lower() == "char":
        json_handler.add_primitive_data_type("array_string_data_types", sbe_field)
    elif sbe_field["data_type"].lower() in ["int8", "int16",
                                            "int32", "int64",
                                            "uint8",
                                            "uint16",
                                            "uint32",
                                            "uint64"] and sbe_field["presence"] == "optional":
        json_handler.add_primitive_data_type("array_number_data_types", sbe_field)
    elif sbe_field["data_type"].lower().endswith("_enum"):
        json_handler.add_custom_data_type("array_enum_data_types", sbe_field["encoding_type"],
                                          sbe_field["data_type"],
                                          sbe_field["structure"])
    elif sbe_field["data_type"].lower().endswith("_set"):
        json_handler.add_custom_data_type("array_set_data_types", sbe_field["encoding_type"],
                                          sbe_field["data_type"],
                                          sbe_field["structure"])


def generate_xml_schema_from_json_schema(json_handler, xml_handler):
    number_data_types = json_handler.get_schema_array_iterator("array_number_data_types")
    for number_data_type in number_data_types:
        xml_handler.generate_sbe_number_definition(number_data_type["name_type"], number_data_type["data_type"],
                                                   number_data_type["presence"])

    string_data_types = json_handler.get_schema_array_iterator("array_string_data_types")
    for string_data_type in string_data_types:
        xml_handler.generate_sbe_string_definition(string_data_type["name_type"], string_data_type["data_type"],
                                                   string_data_type["length"],
                                                   string_data_type["presence"])

    enum_data_types = json_handler.get_schema_array_iterator("array_enum_data_types")
    for enum_data_type in enum_data_types:
        xml_handler.generate_sbe_enum_definition(enum_data_type["encoding_type"], enum_data_type["data_type"],
                                                 enum_data_type["structure"])

    set_data_types = json_handler.get_schema_array_iterator("array_set_data_types")
    for set_data_type in set_data_types:
        xml_handler.generate_sbe_set_definition(set_data_type["encoding_type"], set_data_type["data_type"],
                                                set_data_type["structure"])

    xml_handler.generate_sbe_default_composites()

    document_messages = json_handler.get_schema_array_iterator("array_document_messages")
    for document_message in document_messages:
        xml_handler.generate_sbe_message_xml(
            document_message["message_name"],
            document_message["template_id"],
            json_handler.get_message_array_iterator(document_message["message_name"],
                                                    "array_sbe_fields"),
            json_handler.get_message_array_iterator(document_message["message_name"],
                                                    "array_sbe_repeating_groups")
        )


def add_sbe_field(json_handler, document_message, document_field):
    if document_field.get("group_id", -1) == -1:
        json_handler.add_sbe_field_to_message(
            document_message,
            json.loads(generate_sbe_field(document_field)))
    elif document_field.get("group_id", -1) != -1:
        json_handler.add_sbe_field_to_repeating_group(
            document_message,
            document_field.get("group_id"),
            json.loads(generate_sbe_field(document_field)))


def main():
    st.title("SBE XML Schema Generator")

    tab1, tab2 = st.tabs(["Automatic", "Manual"])

    with tab1:
        st.header("Questo è il Tab 1")
        st.write("Qui puoi inserire il contenuto per il Tab 1.")

    with tab2:
        st.header("Questo è il Tab 2")
        st.write("Qui puoi inserire il contenuto per il Tab 2.")

        tabs = [tab_new_json_schema, tab_new_document_message, tab_new_document_message_column,
                tab_new_document_message_field, tab_new_document_repeating_group, tab_generate_sbe_xml_schema]
        default_index = tabs.index(tab_new_document_message)  # This will dynamically find the index
        tab = st.selectbox("Select Tab", tabs, index=default_index)

        if tab == tab_new_json_schema:
            st.subheader("Create New JSON Schema")
            json_schema_name = st.text_input("Name JSON Schema")
            package = st.text_input("Package")
            description = st.text_input("Description")
            namespace_enx = st.text_input("Namespace ENX")

            namespace_sbe = st.text_input("Namespace SBE", value="http://fixprotocol.io/2016/sbe")
            namespace_str = st.text_input("Namespace STR", value="http://exslt.org/strings")
            namespace_ext = st.text_input("Namespace EXT", value="http://exslt.org/common")
            schema_id = st.text_input("Schema ID", value="25")
            version = st.text_input("Version", value="306")
            semantic_version = st.text_input("Semantic Version", value="4.6.0")
            byte_order = st.text_input("Byte Order", value="littleEndian")

            if json_schema_name:
                if st.button(f"Create JSON Schema File"):
                    try:
                        json_handler = JsonSchemaHandler(namespace_sbe, namespace_enx, namespace_str,
                                                         namespace_ext, package, schema_id, version, semantic_version,
                                                         description, byte_order)
                        st.success(f"Schema '{json_schema_name}' saved successfully.")
                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")

        elif tab == tab_new_document_message:
            st.subheader(tab_new_document_message)
            json_schema_name = st.text_input("Name JSON Schema")
            message_name = st.text_input("Name Document Message")
            template_id = st.number_input("Template ID", value=0, format="%d")

            if json_schema_name and message_name and template_id >= 0:
                json_handler = JsonSchemaHandler(json_schema_name)
                if st.button(f"Create Message in {json_schema_name}"):
                    json_handler.add_document_message(message_name, template_id)
                    st.success(json_handler.load_schema())


        elif tab == tab_new_document_message_column:
            st.subheader(tab_new_document_message_column)
            json_schema_name = st.text_input("Name JSON Schema")
            message_name = st.text_input("Name Document Message")
            column_name = st.text_input("Name Column")

            if json_schema_name and message_name and column_name:
                json_handler = JsonSchemaHandler(json_schema_name)
                if st.button(f"Create Column in {message_name}"):
                    json_handler.add_document_column_to_message(message_name, column_name)
                    st.success(json_handler.load_schema())

        elif tab == tab_new_document_message_field:
            st.subheader(tab_new_document_message_field)
            json_schema_name = st.text_input("Name JSON Schema")
            message_name = st.text_input("Name Document Message")
            group_id = st.text_input("Repeating Group ID",
                                     help="Insert NumInGroup ID if the field belongs to a repeating group, otherwise leave it empty")
            if json_schema_name and message_name:
                json_handler = JsonSchemaHandler(json_schema_name)
                if st.button(f"Show New {message_name}'s Field Form"):
                    if "create_message_field" not in st.session_state:
                        st.session_state["create_message_field"] = True
                    st.session_state["create_message_field"] = True
                if "create_message_field" in st.session_state and st.session_state["create_message_field"] == True:
                    column_iterator = json_handler.get_message_array_iterator(message_name, 'array_document_columns')
                    json_document_field = {}
                    for column in column_iterator:
                        json_document_field[column] = st.text_input(column)
                    json_document_field["additional_information"] = st.text_input("Additional Information")
                    if group_id:
                        json_document_field["group_id"] = group_id
                    if st.button(f"Create New Field in {message_name}"):
                        json_handler.add_document_field_to_message(message_name, json_document_field)
                        st.success(json_handler.load_schema())
                        st.session_state["create_message_field"] = False

        elif tab == tab_new_document_repeating_group:
            st.subheader(tab_new_document_repeating_group)
            json_schema_name = st.text_input("Name JSON Schema")
            message_name = st.text_input("Name Document Message")
            group_name = st.text_input("Name Repeating Group")
            group_id = st.text_input("ID Repeating Group")
            if json_schema_name and message_name and group_name and group_id:
                json_handler = JsonSchemaHandler(json_schema_name)
                if st.button(f"Create New Repeating Group in {message_name}"):
                    json_handler.add_repeating_group_to_message(message_name, group_name, group_id)

        elif tab == tab_new_document_composite:
            st.subheader(tab_new_document_composite)
            json_schema_name = st.text_input("Name JSON Schema")
            name_composite = st.text_input("Name Composite")
            description_composite = st.text_input("Description Composite")
            if json_schema_name and name_composite:
                json_handler = JsonSchemaHandler(json_schema_name)
                if st.button(f"Create New Composite in {json_schema_name}"):
                    json_handler.add_repeating_group_to_message(name_composite, description_composite)


        elif tab == tab_generate_sbe_xml_schema:
            st.subheader(tab_generate_sbe_xml_schema)
            json_schema_name = st.text_input("Name JSON Schema")

            if json_schema_name:
                if st.button("Genera Schema SBE"):
                    json_handler = JsonSchemaHandler(json_schema_name)
                    xml_handler = XmlSbeSchemaHandler(json_schema_name)

                    # lambda_add_sbe_field = lambda document_message, document_field: (
                    #     add_sbe_field(json_handler, document_message, document_field)
                    # )
                    #
                    # json_handler.iterate_document_fields_of_document_messages(lambda_add_sbe_field)

                    lambda_generate_sbe_data_type_definitions = lambda sbe_field: (
                        generate_sbe_data_type_definitions(json_handler, sbe_field)
                    )

                    json_handler.iterate_sbe_fields_of_document_messages(lambda_generate_sbe_data_type_definitions)

                    generate_xml_schema_from_json_schema(json_handler, xml_handler)


# This checks if the script is being run directly (and not imported)
if __name__ == "__main__":
    main()
