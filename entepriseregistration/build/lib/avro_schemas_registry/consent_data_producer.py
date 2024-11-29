import json
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from avro_schemas_registry.producer import  ProducerClass  
#from confluent_kafka.schema_registry.schema import Schema
from avro_schemas_registry.convert_data_to_avro import  generate_schema_from_dict
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema  
import uuid

#schama_registry_client
# Define the AvroProducerClass
def deliverd_report(err, mess):
	if err is not None:
		print(f"Faild to deliver the message {mess.key}")
		return
	print(f"succefuly deliver - {mess.key()} topic {mess.topic}, partition: {mess.partition()}, offset: {mess.offset()}")
	
class AvroProducerClass(ProducerClass):
    def __init__(self, bootstrap_server, topic, schema_registry_client, schema_str):
        super().__init__(bootstrap_server, topic)
        self.schema_registry_client = schema_registry_client
        self.schema_str = schema_str
        self.value_serializer = AvroSerializer(self.schema_registry_client, self.schema_str)

    def send_message(self, message, key):
        try:
            # Serialize the message using Avro
            avro_byte_message = self.value_serializer(
                message, SerializationContext(self.topic, MessageField.VALUE)
            )

            # Assuming schema_json_str and schema_type are set correctly
            schema = Schema(self.schema_str, "AVRO")

            # Produce the Avro message
            self.producer.produce(topic = self.topic, key = key, value=avro_byte_message, headers=[("correlation_id", str(uuid.uuid4()))],on_delivery=deliverd_report)
            print(f"Message Sent: {avro_byte_message}")
        except Exception as e:
            print(f"Error: {e}")

# Function to load the AVRO schema from a file
def load_avro_schema(schema_file):
    with open(schema_file, 'r') as f:
        schema = json.load(f)  # Load JSON from file
    return schema

