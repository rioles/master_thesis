import fastavro
from typing import Any, Dict

def generate_schema_from_dict(data: Dict[str, Any], record_name: str) -> Dict[str, Any]:
    """
    Generates an Avro schema from a dictionary.

    :param data: The dictionary containing data.
    :param record_name: The name of the Avro record.
    :return: A dictionary representing the Avro schema.
    """
    # Mapping of Python types to Avro types
    type_mapping = {
        str: "string",
        int: "int",
        bool: "boolean",
        list: lambda key, value: {"type": "array", "items": "string"},  # Adjust if needed
        dict: lambda key, value: generate_schema_from_dict(value, f"{key}Record")
    }

    # Default values for each type
    default_values = {
        str: "",
        int: 0,
        bool: False,
        list: [],
        dict: {}
    }

    fields = []

    for key, value in data.items():
        field_type = type_mapping.get(type(value))
        if field_type:
            # Use the type of the value to get the default value
            default_value = default_values.get(type(value), None)

            if callable(field_type):  # For list and dict types
                fields.append({"name": key, "type": field_type(key, value), "default": default_value})
            else:  # For base types
                fields.append({"name": key, "type": field_type, "default": default_value})

    return {
        "type": "record",
        "name": record_name,
        "fields": fields
    }

