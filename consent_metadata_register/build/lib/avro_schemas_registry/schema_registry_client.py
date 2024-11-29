from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.error import SchemaRegistryError
import fastavro
import json
import os
from dotenv import load_dotenv
load_dotenv()

class SchemaClient:
    def __init__(self, schema_url, subject_name, schema_str, schema_type):
        self.schema_url = schema_url
        self.subject_name = subject_name
        self.schema_str = schema_str
        self.schema_type = schema_type
        self.schema_client = SchemaRegistryClient({"url": self.schema_url})

    def check_schema_exists(self):
        try:
            self.schema_client.get_latest_version(self.subject_name)
            return True
        except SchemaRegistryError:
            return False

    def register_schema(self):
        try:
            schema_json_str = json.dumps(self.schema_str)
            schema = Schema(schema_json_str, self.schema_type)
            schema_id = self.schema_client.register_schema(self.subject_name, schema)
            print("this is schema registered",schema_id)
        except SchemaRegistryError as e:
            print(e)

    def set_compatibility(self, compatibility):
        try:
            self.schema_client.set_compatibility(self.subject_name, compatibility)
            print(f"schemas compatibility is set to {compatibility}")
        except SchemaRegistryError as e:
            print("schema is not compatible", e)

    def get_schema_version(self):
        try:
            schema_version = self.schema_client.get_latest_version(self.subject_name)
            schema = self.schema_client.get_schema(schema_version.schema_id)
            return schema_version
        except SchemaRegistryError:
            return False

    def get_schema_str(self):
        try:
            schema_version = self.get_schema_version()
            if schema_version:
                schema_id = schema_version.schema_id
                schema = self.schema_client.get_schema(schema_id)
                return schema.schema_str
            else:
                print("Schema version not found")
                return None
        except SchemaRegistryError as e:
            print("Error retrieving schema string:", e)

def load_avro_schema(schema_file):
    with open(schema_file, 'r') as f:
        schema = json.load(f)  # Load JSON from file
    return schema

if __name__ == "__main__":
    schema_file = os.getenv('schema_file')
    #print(schema_file)
    schema_dict = load_avro_schema(schema_file)
    #print(schema_dict)
    schema_url = os.getenv('schema_url')
    topic_name = os.getenv('subject_name')
    schema_json_str = json.dumps(schema_dict)
    schema_type = "AVRO"
    client = SchemaClient(schema_url, topic_name, schema_dict, schema_type)
    client.register_schema()
    client.set_compatibility("FORWARD")

