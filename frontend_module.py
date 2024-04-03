# ai_engine_module.py

import streamlit as st

from json_schema_handler import JsonSchemaHandler
from xml_sbe_schema_handler import XmlSbeSchemaHandler
import utils

tab_new_json_schema = "Add New JSON Schema File"
tab_new_document_message = "Add New Document Message"
tab_new_document_message_column = "Add New Document Message Column"
tab_new_document_message_field = "Add New Document Message Field"
tab_new_document_repeating_group = "Add New Document Repeating Group"
tab_new_document_composite = "Add New Document Composite"
tab_generate_sbe_xml_schema = "Generate SBE XML Schema"

if 'toggle_state' not in st.session_state:
    st.session_state['toggle_state'] = False
if 'pdf_uploaded_state' not in st.session_state:
    st.session_state['pdf_uploaded_state'] = False


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


def form_generate_sbe_xml_schema():
    st.subheader(tab_generate_sbe_xml_schema)

    uploaded_file = st.file_uploader("Carica un file PDF", type="pdf")

    if uploaded_file is not None:
        pdf_path = utils.save_uploaded_file("pdf_documents", uploaded_file)
        st.success(f"File salvato in: {pdf_path}")

        checkbox_label = "Editable PDF" if st.session_state.toggle_state else "Read Only PDF"
        st.checkbox(checkbox_label, key='toggle_state', value=st.session_state.toggle_state)

        json_schema_name = st.text_input(
            "Name JSON Schema",
            key="json_schema_name_form_new_sbe_message"
        )

        if json_schema_name:
            json_handler = JsonSchemaHandler(json_schema_name)
            st.session_state['pdf_uploaded_state'] = True

        if st.session_state['pdf_uploaded_state']:
            if st.button(f"Generate SBE XML Schema \'{json_schema_name}\'"):
                with (st.spinner('Creazione dello Schema SBE XML in corso...')):

                    if not st.session_state['toggle_state']:
                        is_pdf_editable = False
                    elif st.session_state['toggle_state']:
                        is_pdf_editable = True

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


def load_and_display_json():
    name_sbe_schema = st.text_input("Name SBE Schema")

    if name_sbe_schema:
        try:
            json_schema_handler = JsonSchemaHandler(name_sbe_schema)

            edited_content = st.text_area(
                "Modifica JSON Schema:",
                value=json_schema_handler.load_string_schema(),
                height=300,
                key=f"edit_{name_sbe_schema}"
            )

            if st.button("Salva modifiche", key=f"save_{name_sbe_schema}"):
                success, message = json_schema_handler.save_edited_json_schema(edited_content)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        except Exception as e:
            st.error(str(e))
    else:
        st.error("Inserisci un nome valido per lo schema.")


def main():
    st.title("SBE XML Schema Generator")

    tab1, tab2, tab3 = st.tabs(["Automatic", "Manual", "Viewer"])

    with tab1:
        st.header("AI Automatic Generator")
        tabs = [tab_new_json_schema, tab_new_document_message, tab_generate_sbe_xml_schema]
        default_index = tabs.index(tab_new_document_message)
        tab = st.selectbox("Select Tab", tabs, index=default_index)
        if tab == tab_new_json_schema:
            form_new_sbe_schema()
        elif tab == tab_new_document_message:
            form_new_sbe_message()
        elif tab == tab_generate_sbe_xml_schema:
            form_generate_sbe_xml_schema()

    with tab2:
        st.header("Manual Generator")

        tabs = [tab_new_json_schema, tab_new_document_message, tab_new_document_message_column,
                tab_new_document_message_field, tab_new_document_repeating_group, tab_generate_sbe_xml_schema]
        default_index = tabs.index(tab_new_document_message)  # This will dynamically find the index
        tab = st.selectbox("Select Tab", tabs, index=default_index)

        if tab == tab_new_json_schema:
            form_new_sbe_schema()

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

                    lambda_generate_sbe_fields = lambda document_message: (
                        json_handler.generate_sbe_fields(document_message)
                    )

                    json_handler.iterate_document_messages(lambda_generate_sbe_fields)

                    lambda_generate_sbe_data_type_definitions = lambda sbe_field: (
                        json_handler.generate_sbe_data_type_definitions(sbe_field)
                    )

                    json_handler.iterate_sbe_fields_of_document_messages(lambda_generate_sbe_data_type_definitions)

                    xml_handler.generate_xml_schema_from_json_schema(json_handler)

    with tab3:
        load_and_display_json()


# This checks if the script is being run directly (and not imported)
if __name__ == "__main__":
    main()
