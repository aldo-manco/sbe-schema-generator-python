import json
import logging
from pathlib import Path

import ai_engine_module
from utils import utils


class JsonSchemaHandler:
    def __init__(
            self,
            json_schema_name,
            namespace_sbe=None,
            namespace_enx=None,
            namespace_str=None,
            namespace_ext=None,
            package=None,
            schema_id=None,
            version=None,
            semantic_version=None,
            description=None,
            byte_order=None,
            suffix_name="_json_schema"
    ):
        self.json_schema_name = json_schema_name.lower()
        self.suffix_name = suffix_name.lower()
        self.directory_name = "output"
        self.file_name = f"{self.json_schema_name}{self.suffix_name}.json"
        self.file_path = Path(self.directory_name, self.file_name)

        if namespace_sbe and namespace_enx and namespace_str and namespace_ext and package and schema_id and version and semantic_version and description and byte_order:
            self.namespace_sbe = namespace_sbe.lower()
            self.namespace_enx = namespace_enx.lower()
            self.namespace_str = namespace_str.lower()
            self.namespace_ext = namespace_ext.lower()
            self.package = package.lower()
            self.schema_id = schema_id
            self.version = version
            self.semantic_version = semantic_version
            self.description = description
            self.byte_order = byte_order

            self.create_new_file_json_schema()

        self.schema = self.load_schema()

    def load_schema(self):
        try:
            return json.loads(self.file_path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            raise KeyError(f"JSON SBE schema file '{self.file_path}' not found.")
        except json.JSONDecodeError:
            return None, "Error in the JSON SBE Parsing."

    def load_string_schema(self):
        return json.dumps(self.load_schema(), indent=4)

    def create_new_file_json_schema(self):
        utils.create_directory_if_not_exists(self.directory_name)
        file_content = {
            self.json_schema_name: {
                "namespace_sbe": self.namespace_sbe,
                "namespace_enx": self.namespace_enx,
                "namespace_str": self.namespace_str,
                "namespace_ext": self.namespace_ext,
                "package": self.package,
                "schema_id": self.schema_id,
                "version": self.version,
                "semantic_version": self.semantic_version,
                "description": self.description,
                "byte_order": self.byte_order,
                "array_number_data_types": [],
                "array_string_data_types": [],
                "array_enum_data_types": [],
                "array_set_data_types": [],
                "array_document_messages": []
            }
        }

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(file_content, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"An error occurred while writing to {self.file_path}: {e}")

    def add_document_message(
            self,
            message_name,
            template_id,
            starting_page=0,
            ending_page=0
    ):
        if self.json_schema_name not in self.schema:
            raise KeyError(f"JSON schema '{self.json_schema_name}' not found.")

        for document_message in self.get_schema_array_iterator("array_document_messages"):
            if (document_message["message_name"] == message_name
                    or document_message["template_id"] == template_id):
                print(f"Message \'{message_name}\' already exists in the JSON schema \'{self.json_schema_name}\'")
                return

        new_document_message = {
            "message_name": message_name,
            "template_id": template_id,
            "array_sbe_fields": [],
            "array_sbe_repeating_groups": []
        }

        if starting_page != 0 and ending_page != 0:
            new_document_message["starting_page"] = starting_page
            new_document_message["ending_page"] = ending_page

        self.schema[self.json_schema_name]['array_document_messages'].append(new_document_message)
        self.save_schema()

    def get_json_schema_field(
            self,
            name_field
    ):
        if self.json_schema_name not in self.schema:
            raise KeyError(f"JSON schema '{self.json_schema_name}' not found.")

        return self.schema[self.json_schema_name][name_field]

    def get_schema_array_iterator(
            self,
            array_schema
    ):
        if self.json_schema_name not in self.schema:
            raise KeyError(f"JSON schema '{self.json_schema_name}' not found.")

        return iter(
            self.schema[self.json_schema_name][array_schema]
        )

    def find_document_message_in_json_schema(
            self,
            message_key
    ):
        for message in self.get_schema_array_iterator('array_document_messages'):
            if message.get("message_name") == message_key:
                return message

        return None

    def get_message_array_iterator(
            self,
            message_key,
            array_in_document_message
    ):
        message = self.find_document_message_in_json_schema(message_key)
        if message is None:
            raise KeyError(f"Message '{message_key}' not found in schema.")

        return iter(
            message.get(
                array_in_document_message,
                []
            )
        )

    def iterate_document_messages(
            self,
            process_field_function
    ):
        document_messages = self.get_schema_array_iterator("array_document_messages")

        for document_message in document_messages:
            process_field_function(document_message)

    def add_sbe_field_to_message(
            self,
            message_key,
            json_sbe_field
    ):
        message = self.find_document_message_in_json_schema(message_key)
        if message is None:
            raise KeyError(f"Message '{message_key}' not found in schema.")

        if json_sbe_field in self.get_message_array_iterator(
                message_key,
                'array_sbe_fields'
        ):
            print(
                f"SBE Field already exists in the message '{message_key}' of the JSON schema '{self.json_schema_name}'")
            return

        message['array_sbe_fields'].append(json_sbe_field)
        self.save_schema()

    def iterate_sbe_fields_of_document_messages(
            self,
            process_field_function
    ):
        document_messages = self.get_schema_array_iterator("array_document_messages")

        for document_message in document_messages:
            sbe_fields = self.get_message_array_iterator(
                document_message["message_name"],
                "array_sbe_fields"
            )

            for sbe_field in sbe_fields:
                process_field_function(sbe_field)

            repeating_groups = self.get_message_array_iterator(
                document_message["message_name"],
                "array_sbe_repeating_groups"
            )

            for repeating_group in repeating_groups:
                sbe_fields = iter(
                    repeating_group.get(
                        "items",
                        []
                    )
                )

                for sbe_field in sbe_fields:
                    process_field_function(sbe_field)

    def add_repeating_group_to_message(
            self,
            message_key,
            group_name,
            group_tag_number
    ):
        message = self.find_document_message_in_json_schema(message_key)
        if message is None:
            raise KeyError(f"Message '{message_key}' not found in schema.")

        for repeating_group in self.get_message_array_iterator(
                message_key,
                "array_sbe_repeating_groups"
        ):
            if repeating_group["group_name"] == group_name:
                print(
                    f"Repeating Group {group_name} already exists in the message '{message_key}' of the JSON schema '{self.json_schema_name}'")
                return

        new_repeating_group = {}

        if group_tag_number != -1:
            new_repeating_group["group_tag_number"] = group_tag_number

        new_repeating_group["group_name"] = group_name
        new_repeating_group["items"] = []

        message["array_sbe_repeating_groups"].append(new_repeating_group)
        self.save_schema()

    def add_sbe_field_to_repeating_group(self, message_key, repeating_group_name, json_sbe_field):
        message = self.find_document_message_in_json_schema(message_key)
        if message is None:
            raise KeyError(f"Message '{message_key}' not found in schema.")

        for repeating_group in self.get_message_array_iterator(
                message_key,
                "array_sbe_repeating_groups"
        ):
            if repeating_group["group_name"] == repeating_group_name:
                already_exists = False
                if json_sbe_field in repeating_group["items"]:
                    already_exists = True
                if not already_exists:
                    repeating_group["items"].append(json_sbe_field)
                    self.save_schema()
                    break
                else:
                    print(f"Repeating group's SBE field already exists.")
        else:
            print(f"Repeating group {repeating_group_name} not found.")

    def add_alphanumeric_data_type(
            self,
            sbe_field
    ):
        sbe_field["custom_type"] = ""

        if sbe_field["presence"] == "optional":
            sbe_field["custom_type"] = f"{sbe_field['data_type']}{sbe_field['length']}_{sbe_field['presence']}"
        else:
            sbe_field["custom_type"] = f"{sbe_field['data_type']}{sbe_field['length']}"

        if self.is_alphanumeric_data_type_exists_in_json_schema(
                sbe_field["data_type"],
                sbe_field["presence"],
                sbe_field["length"],
        ):
            print(
                f"Data Type \'{sbe_field['data_type']}\' already exists in the JSON schema \'{self.json_schema_name}\'")
            return

        new_primitive_data_type = {
            "name_type": sbe_field["custom_type"],
            "data_type": sbe_field["data_type"],
            "presence": sbe_field["presence"],
            "length": sbe_field["length"]
        }

        self.schema[self.json_schema_name]["array_string_data_types"].append(new_primitive_data_type)
        self.save_schema()

    def add_numeric_data_type(self, sbe_field):
        sbe_field["custom_type"] = f"{sbe_field['data_type']}_t"

        if self.is_numeric_data_type_exists_in_json_schema(
                sbe_field["data_type"],
                sbe_field["presence"]
        ):
            print(
                f"Data Type \'{sbe_field['data_type']}\' already exists in the JSON schema \'{self.json_schema_name}\'")
            return

        new_primitive_data_type = {
            "name_type": sbe_field["custom_type"],
            "data_type": sbe_field["data_type"],
            "presence": sbe_field["presence"]
        }

        self.schema[self.json_schema_name]["array_number_data_types"].append(new_primitive_data_type)
        self.save_schema()

    def is_alphanumeric_data_type_exists_in_json_schema(
            self,
            data_type_to_find,
            presence,
            length
    ):
        for data_type in self.get_schema_array_iterator("array_string_data_types"):
            if (data_type.get("data_type") == data_type_to_find
                    and data_type.get("length") == length
                    and data_type.get("presence") == presence
            ):
                return True

        return False

    def is_numeric_data_type_exists_in_json_schema(self, data_type_to_find, presence):
        for data_type in self.get_schema_array_iterator("array_number_data_types"):
            if data_type.get("data_type") == data_type_to_find and data_type.get(
                    "presence") == presence:
                return True

        return False

    def add_custom_data_type(
            self,
            array_custom_data_type,
            data_type,
            possible_values,
            encoding_type
    ):
        if self.is_custom_data_type_exists_in_json_schema(
                array_custom_data_type,
                data_type,
                possible_values
        ):
            print(f"Data Type \'{data_type}\' already exists in the JSON schema \'{self.json_schema_name}\'")
            return

        new_custom_data_type = {
            "data_type": data_type,
            "possible_values": possible_values,
            "encoding_type": encoding_type
        }

        self.schema[self.json_schema_name][array_custom_data_type].append(new_custom_data_type)
        self.save_schema()

    def is_custom_data_type_exists_in_json_schema(
            self,
            array_custom_data_type,
            data_type_to_find,
            possible_values
    ):
        for data_type in self.get_schema_array_iterator(array_custom_data_type):
            if data_type.get("data_type") == data_type_to_find:
                data_type["possible_values"] = {**possible_values, **data_type["possible_values"]}
                return True

        return False

    def generate_sbe_data_type_definitions(
            self,
            sbe_field
    ):
        array_numeric_data_types = [
            "int8",
            "int16",
            "int32",
            "int64",
            "uint8",
            "uint16",
            "uint32",
            "uint64"
        ]

        array_alphanumeric_data_types = [
            "char"
        ]

        logging.info(f"DICTDICTDICT: {sbe_field}")

        if sbe_field["data_type"].lower() in array_alphanumeric_data_types:
            self.add_alphanumeric_data_type(
                sbe_field
            )

        elif (sbe_field["data_type"].lower() in array_numeric_data_types
              and sbe_field["presence"] == "optional"):
            self.add_numeric_data_type(
                sbe_field
            )

        elif sbe_field["data_type"].lower().endswith("_enum"):
            self.add_custom_data_type(
                "array_enum_data_types",
                sbe_field["data_type"],
                sbe_field["possible_values"],
                sbe_field["encoding_type"]
            )

        elif sbe_field["data_type"].lower().endswith("_set"):
            self.add_custom_data_type(
                "array_set_data_types",
                sbe_field["data_type"],
                sbe_field["possible_values"],
                sbe_field["encoding_type"]
            )

    def save_schema(self):
        self.file_path.write_text(
            json.dumps(
                self.schema,
                indent=4,
                ensure_ascii=False
            ),
            encoding='utf-8'
        )

    def generate_sbe_message(
            self,
            document_message,
            pdf_path,
            is_pdf_editable
    ):
        message_name = document_message["message_name"]
        starting_page = document_message["starting_page"]
        ending_page = document_message["ending_page"]

        json_array_sbe_fields, json_array_repeating_groups = ai_engine_module.process(
            pdf_path,
            starting_page,
            ending_page,
            is_pdf_editable
        )

        for sbe_field in json_array_sbe_fields:
            self.add_sbe_field_to_message(
                message_name,
                sbe_field
            )

        for repeating_group in json_array_repeating_groups:
            self.add_repeating_group_to_message(
                message_name,
                repeating_group["group_name"],
                repeating_group["group_tag_number"] if "group_tag_number" in repeating_group else -1
            )

            for sbe_field in repeating_group["items"]:
                self.add_sbe_field_to_repeating_group(
                    message_name,
                    repeating_group["group_name"],
                    sbe_field
                )
