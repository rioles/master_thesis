from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import Producer
from avro_schemas_registry.admin_topik_kafka import KafkaAdmin

class ProducerClass():
    def __init__(self, bootstrap_server, topic, message_size=None, compression_type="gzip", batch_size=16384, linger_ms=100):
        """
        Initializes a Kafka producer with the specified configuration.

        Args:
            bootstrap_server (str): The address of the Kafka bootstrap server.
            topic (str): The Kafka topic to which the messages will be sent.
            message_size (int, optional): Maximum message size in bytes. Default is None.
            compression_type (str, optional): The compression algorithm to use. Default is 'gzip'.
                Valid options: 'gzip', 'snappy', 'lz4', 'zstd', 'none'.
            batch_size (int, optional): Maximum size of message batches in bytes before sending to Kafka. 
                Default is 16KB (16384 bytes).
            linger_ms (int, optional): The maximum time (in milliseconds) the producer will wait 
                to accumulate a batch before sending it to Kafka. Default is 100ms.
        """
        self.bootstrap_server = bootstrap_server
        self.topic = topic
        
        # Configuration dictionary for the Kafka producer
        config = {'bootstrap.servers': self.bootstrap_server}
        
        if message_size is not None:
            config['message.max.bytes'] = message_size
        
        config['compression.type'] = compression_type
        config['batch.size'] = batch_size
        config['linger.ms'] = linger_ms
        
        self.producer = Producer(config)
    
    def send_message(self, message):
        """
        Sends a message to the specified Kafka topic.
        
        Args:
            message (str): The message to send.
        """
        try:
            self.producer.produce(self.topic, value=message)
        except Exception as e:
            print(f"Error producing message: {e}")
    
    def commit(self):
        """
        Flushes any remaining messages in the producer's buffer to the Kafka broker.
        Ensures that all messages are sent before closing the producer.
        """
        self.producer.flush()

    
    def send_message(self, message):
        """
        Sends a message to the specified Kafka topic.
        
        Args:
            message (str): The message to send.
        """
        try:
            self.producer.produce(self.topic, value=message)
        except Exception as e:
            print(f"Error producing message: {e}")
    
    def commit(self):
        """
        Flushes any remaining messages in the producer's buffer to the Kafka broker.
        Ensures that all messages are sent before closing the producer.
        """
        self.producer.flush()


