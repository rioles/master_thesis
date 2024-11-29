import os
import json
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
from avro_schemas_registry.schema_registry_client import SchemaClient
from message_queue_config.rabbitmq import RabbitMQ, appli
import fastavro
import json
from dotenv import load_dotenv
load_dotenv()
from models import storage


class ConsumerGroupClass:
    def __init__(self,rabbit_mq, bootstrap_servers,task_name, queue_name, topic, schema_client, schema_str, group_id="8956", auto_offset_reset='earliest'):
        """
        Initialize the consumer group configuration.
        
        :param bootstrap_servers: Kafka broker (e.g., "localhost:9092")
        :param topic: Kafka topic to subscribe to
        :param group_id: Consumer group ID
        :param schema_client: Schema registry client
        :param schema_str: Schema string to deserialize messages
        :param auto_offset_reset: Offset reset strategy ("earliest", "latest")
        """
        self.rabbit_mq = rabbit_mq
        self.bootstrap_servers = bootstrap_servers
        self.task_name = task_name
        self.queue_name = queue_name
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
                self.rabbit_mq.publish_message(self.task_name, self.queue_name, **message_deserialized)

        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

def load_avro_schema(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def return_consumer_object():
    schema_file = os.getenv('schema_file')
    print(schema_file)
    schema_url = os.getenv('schema_url')
    topic_name = os.getenv('topic_name_0')
    subject_name = os.getenv('subject_name')
    bootstrap_server = os.getenv('bootstrap_server')
    schema_dict = load_avro_schema(schema_file)
    schema_json_str = json.dumps(schema_dict)
    schema_type = "AVRO"
    client = SchemaClient(schema_url, subject_name, schema_dict, schema_type)
    rabbitmq = RabbitMQ(appli)
    schema = client.get_schema_str()
    consumer = ConsumerGroupClass(rabbitmq, bootstrap_server, "webhook_sender", "webhook_data", topic_name, client.schema_client, schema)
    # bootstrap_servers, topic, schema_client, schema_str
    consumer.consume_messages()
    print(schema)

if __name__ == "__main__":
    return_consumer_object()
