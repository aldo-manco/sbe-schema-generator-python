# ai_engine_module.py

import streamlit as st

from json_schema_handler import JsonSchemaHandler
from xml_sbe_schema_handler import XmlSbeSchemaHandler
from utils import utils

name_software = "Gatelab AI Engine"
favicon_software_path = "logo/euronext.png"
tab_new_json_schema = "Add New JSON Schema File"
tab_new_document_message = "Add New Document Message"
tab_new_document_message_column = "Add New Document Message Column"
tab_new_document_message_field = "Add New Document Message Field"
tab_new_document_repeating_group = "Add New Document Repeating Group"
tab_new_document_composite = "Add New Document Composite"
tab_generate_sbe_xml_schema_from_pdf = "Generate SBE XML Schema From PDF"
tab_generate_sbe_xml_schema_from_json = "Generate SBE XML Schema From JSON"

st.set_page_config(
    page_title=name_software,
    page_icon=favicon_software_path,
)

if 'toggle_state' not in st.session_state:
    st.session_state['toggle_state'] = True
if 'pdf_uploaded_state' not in st.session_state:
    st.session_state['pdf_uploaded_state'] = False
if 'json_uploaded_state' not in st.session_state:
    st.session_state['json_uploaded_state'] = False


def form_new_sbe_schema():
    st.subheader("Create New JSON Schema")

    json_schema_name = st.text_input(
        "Name JSON Schema",
        key="json_schema_name_form_new_sbe_schema"
    )
    package = st.text_input(
        "Package",
        key="package_form_new_sbe_schema"
    )
    description = st.text_input(
        "Description",
        key="description_form_new_sbe_schema"
    )
    namespace_enx = st.text_input(
        "Namespace ENX",
        key="namespace_enx_form_new_sbe_schema"
    )
    namespace_sbe = st.text_input(
        "Namespace SBE",
        key="namespace_sbe_form_new_sbe_schema",
        value="http://fixprotocol.io/2016/sbe"
    )
    namespace_str = st.text_input(
        "Namespace STR",
        key="namespace_str_form_new_sbe_schema",
        value="http://exslt.org/strings"
    )
    namespace_ext = st.text_input(
        "Namespace EXT",
        key="namespace_ext_form_new_sbe_schema",
        value="http://exslt.org/common"
    )
    schema_id = st.text_input(
        "Schema ID",
        key="schema_id_form_new_sbe_schema",
        value="25"
    )
    version = st.text_input(
        "Version",
        key="version_form_new_sbe_schema",
        value="306"
    )
    semantic_version = st.text_input(
        "Semantic Version",
        key="semantic_version_form_new_sbe_schema",
        value="4.6.0"
    )
    byte_order = st.text_input(
        "Byte Order",
        key="byte_order_form_new_sbe_schema",
        value="littleEndian"
    )

    if json_schema_name:
        if st.button(f"Create JSON Schema File"):
            try:
                JsonSchemaHandler(
                    json_schema_name,
                    namespace_sbe,
                    namespace_enx,
                    namespace_str,
                    namespace_ext,
                    package,
                    schema_id,
                    version,
                    semantic_version,
                    description,
                    byte_order
                )
                st.success(f"Schema '{json_schema_name}' saved successfully.")
            except Exception as e:
                st.error(f"Error saving file: {str(e)}")


def toggle_action():
    st.session_state['toggle_state'] = not st.session_state['toggle_state']


def form_new_sbe_message():
    st.subheader(tab_new_document_message)

    json_schema_name = st.text_input(
        "Name JSON Schema",
        key="json_schema_name_form_new_sbe_message"
    )
    message_name = st.text_input(
        "Name Document Message",
        key="message_name_form_new_sbe_message"
    )
    template_id = st.number_input(
        "Template ID",
        key="template_id_form_new_sbe_message",
        value=0,
        format="%d"
    )
    starting_page = st.number_input(
        "Pagina di inizio della tabella",
        key="starting_page_form_new_sbe_message",
        min_value=1,
        format="%d"
    )
    ending_page = st.number_input(
        "Pagina di fine della tabella",
        key="ending_page_form_new_sbe_message",
        min_value=1,
        format="%d"
    )

    if json_schema_name and message_name and template_id >= 0 and starting_page >= 0 and ending_page >= 0:
        st.write(f"Name SBE Message: {message_name}")
        st.write(f"Template ID: {template_id}")
        st.write(f"Starting Page of Table: {starting_page}")
        st.write(f"Ending Page of Table: {ending_page}")

        json_handler = JsonSchemaHandler(json_schema_name)

        if st.button(f"Create Message in {json_schema_name}"):
            json_handler.add_document_message(message_name, template_id, starting_page, ending_page)
            st.success(f"SBE Message \'{message_name}\' is in the SBE Schema \'{json_schema_name}\'")


def form_generate_sbe_xml_schema_from_pdf():
    st.subheader(tab_generate_sbe_xml_schema_from_pdf)

    uploaded_file = st.file_uploader("Carica un file PDF", type="pdf")

    if uploaded_file is not None:
        pdf_path = utils.save_uploaded_file("../pdf_documents", uploaded_file)
        st.success(f"File salvato in: {pdf_path}")

        checkbox_label = "Editable PDF" if st.session_state.toggle_state else "Read Only PDF"
        st.checkbox(checkbox_label, key='toggle_state', value=st.session_state.toggle_state)

        json_schema_name = st.text_input(
            "Name JSON Schema",
            key="json_schema_name_form_generate_sbe_xml_schema_from_pdf"
        )

        if json_schema_name:
            st.session_state['pdf_uploaded_state'] = True

        if st.session_state['pdf_uploaded_state']:
            if st.button(f"Generate SBE XML Schema \'{json_schema_name}\'"):
                with (st.spinner('Creazione dello Schema SBE XML in corso...')):

                    if not st.session_state['toggle_state']:
                        is_pdf_editable = False
                    elif st.session_state['toggle_state']:
                        is_pdf_editable = True

                    json_handler = JsonSchemaHandler(json_schema_name)

                    lambda_generate_sbe_message = lambda document_message: (
                        json_handler.generate_sbe_message(document_message, pdf_path, is_pdf_editable)
                    )

                    json_handler.iterate_document_messages(lambda_generate_sbe_message)

                    lambda_generate_sbe_data_type_definitions = lambda sbe_field: (
                        json_handler.generate_sbe_data_type_definitions(sbe_field)
                    )

                    json_handler.iterate_sbe_fields_of_document_messages(
                        lambda_generate_sbe_data_type_definitions)

                    xml_handler = XmlSbeSchemaHandler(json_schema_name)
                    xml_handler.generate_xml_schema_from_json_schema(json_handler)

                st.success('Schema SBE XML Generato con successo.')

    else:
        st.info("Per favore, seleziona un file PDF.")


def form_generate_sbe_xml_schema_from_json():
    st.subheader(tab_generate_sbe_xml_schema_from_json)

    json_schema_name = st.text_input(
        "Name JSON Schema",
        key="json_schema_name_form_generate_sbe_xml_schema_from_json"
    )

    if json_schema_name:
        st.session_state['json_uploaded_state'] = True

    if st.session_state['json_uploaded_state']:
        if st.button(f"Generate SBE XML Schema \'{json_schema_name}\'"):

            json_handler = JsonSchemaHandler(json_schema_name)

            xml_handler = XmlSbeSchemaHandler(json_schema_name)
            xml_handler.generate_xml_schema_from_json_schema(json_handler)

            st.success('Schema SBE XML Generato con successo.')


def main():
    st.title(name_software)
    st.header("SBE XML Schema AI Generator")
    tabs = [tab_new_json_schema, tab_new_document_message, tab_generate_sbe_xml_schema_from_pdf, tab_generate_sbe_xml_schema_from_json]
    default_index = tabs.index(tab_new_document_message)
    tab = st.selectbox("Select Tab", tabs, index=default_index)

    if tab == tab_new_json_schema:
        form_new_sbe_schema()
    elif tab == tab_new_document_message:
        form_new_sbe_message()
    elif tab == tab_generate_sbe_xml_schema_from_pdf:
        form_generate_sbe_xml_schema_from_pdf()
    elif tab == tab_generate_sbe_xml_schema_from_json:
        form_generate_sbe_xml_schema_from_json()


if __name__ == "__main__":
    main()
