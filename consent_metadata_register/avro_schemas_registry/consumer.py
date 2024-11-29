import os
import json
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
from avro_schemas_registry.schema_registry_client import SchemaClient
from avro_schemas_registry.convert_data_to_avro import  generate_schema_from_dict

import fastavro
import json
from dotenv import load_dotenv
load_dotenv()
from models import storage


class ConsumerGroupClass:
    def __init__(self, bootstrap_servers, topic, group_id, schema_client, schema_str, auto_offset_reset='earliest'):
        """
        Initialize the consumer group configuration.
        
        :param bootstrap_servers: Kafka broker (e.g., "localhost:9092")
        :param topic: Kafka topic to subscribe to
        :param group_id: Consumer group ID
        :param schema_client: Schema registry client
        :param schema_str: Schema string to deserialize messages
        :param auto_offset_reset: Offset reset strategy ("earliest", "latest")
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset
        self.schema_str = schema_str
        self.schema_client = schema_client

        # Kafka consumer configuration
        self.consumer_conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': self.auto_offset_reset,
        }
        
        # Initialize the consumer
        self.consumer = Consumer(self.consumer_conf)
        
        # Initialize the Avro deserializer
        self.value_deserializer = AvroDeserializer(self.schema_client, self.schema_str)

    def subscribe(self):
        """
        Subscribe the consumer to the topic.
        """
        self.consumer.subscribe([self.topic])

    def process_message(self, message):
        """
        Define how to process the received message.
        Override this method in subclasses if needed for custom processing.
        
        :param message: The message (e.g., video data) received from Kafka.
        """
        print(f"Consumed message: {message}")
        
        	
        # Custom logic to process the message (e.g., transcode video)

    def consume_messages(self):
        """
        Consume messages from the Kafka topic and process them.
        """
        self.subscribe()
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Error while consuming message: {msg.error()}")
                    continue

                print(f"Message Consumed: {msg.value()} type is {type(msg.value())}")
                
                # Deserialize the message using AvroDeserializer
                message_deserialized = self.value_deserializer(
                    msg.value(), SerializationContext(self.topic, MessageField.VALUE)
                )
                
                print(f"Message Deserialized: {message_deserialized} type is {type(message_deserialized)}")
                
                # Process the message (custom processing logic)
                self.process_message(message_deserialized)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

	
	
# Load Avro schema (mock function - replace with actual schema loading)
def load_avro_schema(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    # Environment variables
    schema_file = os.getenv('schema_file')
    schema_url = os.getenv('schema_url')
    subject_name = os.getenv('subject_name')
    topic = os.getenv('topic_name')
    
    bootstrap_server = os.getenv('bootstrap_server')
    
    if not all([schema_file, schema_url, topic_name, topic, bootstrap_server]):
        raise ValueError("Missing required environment variables.")
    
    # Load schema and set up the schema client (mock client - replace with actual SchemaClient)
    schema_dict = load_avro_schema(schema_file)
    schema_json_str = json.dumps(schema_dict)
    
    # Assume SchemaClient is implemented elsewhere
    client = SchemaClient(schema_url, subject_name, schema_json_str, "AVRO")
    client.set_compatibility("FORWARD")
    schema = client.get_schema_str()
    print(schema)
    
    # Instantiate the consumer group and start consuming messages
    consumer = ConsumerGroupClass(bootstrap_server, topic, "78945", client.schema_client, schema)
    consumer.consume_messages()
	
