import pika
import json
import logging
import os
import requests
from celery import current_app
from celery import Celery
from celery.utils.log import get_task_logger
from message_queue_config.message_queue import MessageQueue  # Assuming correct import path
from message_queue_config.rabbitmq import RabbitMQ
from models import storage
from celery.utils.log import get_task_logger
from services.get_user_url import GenerateWebhookSignature
from kombu import Connection, Exchange, Queue
from kombu.mixins import ConsumerMixin
from avro_schemas_registry.schema_registry_client import SchemaClient
from avro_schemas_registry.consent_data_producer import AvroProducerClass

# Initialize logger
logger = get_task_logger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
appli = Celery('webhook_processor', broker='amqp://guest@localhost:5672//', backend='rpc://')

BROKER_URL = "amqp://guest:guest@localhost:5672/%2F"
QUEUE_NAME = 'webhook_data'
ERASE_QUEUE_NAME = 'delete_ds_data'
USER_DATA_QUEUE_NAME = 'user_data'

def send_dat_to_webhook(all_data):
    try:
        client_id = all_data["data"]["client"]["client_id"]
        #client_id = id.split("_")
        webhook_url = storage.get(client_id)["client_ressour_url"]
        print("webhook_url",webhook_url)
        if not webhook_url:
            raise ValueError(f"Webhook URL not found for client_id: {client_id}")

        # Generate headers
        if "message" in all_data:
            signature = GenerateWebhookSignature(client_id, all_data["message"])
        else:
            signature = GenerateWebhookSignature(client_id, all_data["data"])
        headers = signature.generate_webhook_header()

        # Send request
        response = requests.post(webhook_url, json=all_data, headers=headers)
        logger.info(f"Webhook response: {response.status_code}, {response.text}")
        return response
    except Exception as e:
        print(e)
        logger.error(f"Error in send_dat_to_webhook: {e}")
        raise

def validity_expire(data):
    all_data = {"data": data}
    message = {
    	"event": "consent_expired",
        "status": 204,
        "data": [],
        "message": "Consent date is expired or no permission grant or erase flag is set to True"
    }
    all_data["message"] = message
    print("this is validity",all_data)
    send_dat_to_webhook(all_data)
    #print(send_dat_to_webhook(all_data))

def send_to_kafka(data):
    all_data = {"data": data} 
    if "consent_grant" in data:
        try:
            logger.info(f"Sending data to Kafka: {data}")
            send_data_to_topic(data)
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {e}")
            raise

        

def load_avro_schema(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)
     	
def send_data_to_topic(data):
    try:
        schema_file = os.getenv('schema_file')
        schema_url = os.getenv('schema_url')
        topic_name = os.getenv('topic_name')
        subject_name = os.getenv('subject_name')
        bootstrap_server = os.getenv('bootstrap_server')

        schema_dict = load_avro_schema(schema_file)
        client = SchemaClient(schema_url, subject_name, schema_dict, "AVRO")
        client.set_compatibility("FORWARD")
        schema = client.get_schema_str()

        producer = AvroProducerClass(bootstrap_server, topic_name, client.schema_client, schema)
        producer.send_message(data, data["client"]["client_id"])
        producer.commit()
    except Exception as e:
        logger.error(f"Error in send_data_to_topic: {e}")
        raise        


        
        
@appli.task(name="process_data")
def process_data(data):
    try:
        if data.get("validity") is False:
            print("Processing invalid data", data)
            validity_expire(data)
        else:
            print("Processing valid data")
            # Uncomment and implement send_to_kafka if needed
            send_to_kafka(data)
    except Exception as e:
        logger.error(f"Error in processing data: {e}")
        #self.retry(exc=e, countdown=1)

@appli.task(name="process_erased_data")
def process_erased_data(data):
    print(data)

    try:
        id_client = None
          
        id = data.get("id", 8)
        if isinstance(id, str) and "_" in id:
            id_client = id.split("_")[1]    
        else:
            id_client = str(id)
            
            
            
        
        webhook_url = json.loads(storage.get(id_client))["cmd_url"]  # Assuming client_id is defined elsewhere

        if not webhook_url:
            raise ValueError(f"Webhook URL not found for client_id: {client_id}")

        signature = GenerateWebhookSignature(id_client, data)
        headers = signature.generate_webhook_header()
        response = requests.post(webhook_url, json=data, headers=headers)
        logger.info(f"Webhook response: {response.status_code}, {response.text}")
        return response

    except Exception as e:
        logger.error(f"Error in process_erased_data: {e}")
        raise  # Re-raise the exception to propagate it
        

@appli.task(name="send_user_data")
def send_user_data(data):
    print(data)

    try:
        id_client = data.get("client_id", "ozana-82df06aa132847b8972cc0d83c589411")  
        id_user = data["user_anip"]
        webhook_url = json.loads(storage.get(id_client))["client_ressour_url"]  # Assuming client_id is defined elsewhere

        if not webhook_url:
            raise ValueError(f"Webhook URL not found for client_id: {client_id}")

        signature = GenerateWebhookSignature(id_client, data)
        headers = signature.generate_webhook_header()
        response = requests.post(webhook_url, json=data, headers=headers)
        logger.info(f"Webhook response: {response.status_code}, {response.text}")
        return response

    except Exception as e:
        logger.error(f"Error in process_erased_data: {e}")
        raise  # Re-raise the exception to propagate it
        

        
def send_erased_notification(ch, method, properties, body):
    """
    Callback function to process messages from the queue with error handling.
    """
    try:
        print("Callback triggered.")
        # Decode and load the JSON message
        body_str = body.decode('utf-8')
        message = json.loads(body_str)
        print(f"Received message: {body_str}")
        print(f"Received message_dict: {message}")
        #r = appli.delay('process_erased_data', args=[message])
        #process_data(message)
        # Acknowledge the message as processed
        process_erased_data(message[1])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
        # Reject the message and requeue it for another attempt
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)        

#def send_delete_data(ch, method, properties, body):
    


def send_webhook_data(ch, method, properties, body):
    try:
        logger.info("Callback triggered.")

        # Decode and load the JSON message
        body_str = body.decode('utf-8')
        message = json.loads(body_str)
        
        # Assuming message is a list and we want the second item
        if isinstance(message, list) and len(message) > 1:
            data = message[1]
        elif isinstance(message, dict):
            data = message
        else:
            raise ValueError("Invalid message format.")

        # Enqueue Celery task
        
        task = process_data.delay(data)
        logger.info(f"Task enqueued: {task.id}")
        process_data(data)
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
        # Reject the message and requeue it for another attempt
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        # Reject the message and requeue it for another attempt
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def send_user_personal_data(ch, method, properties, body):
    """
    Callback function to process messages from the queue with error handling.
    """
    try:
        print("Callback triggered.")
        # Decode and load the JSON message
        body_str = body.decode('utf-8')
        message = json.loads(body_str)
        print(f"Received message: {body_str}")
        print(f"Received message_dict: {message}")
        #r = appli.delay('process_erased_data', args=[message])
        #process_data(message)
        # Acknowledge the message as processed
        send_user_data(message[1])
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
        # Reject the message and requeue it for another attempt
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def get_data(data):
	print("this is the data", data)
	process_data.delay(data)

def consume_message():
    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # Start consuming messages
        logger.info("Starting RabbitMQ consumer...")
        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=send_webhook_data,
            auto_ack=False  # We handle acknowledgments manually
        )
        
        channel.basic_consume(
            queue=ERASE_QUEUE_NAME,
            on_message_callback=send_erased_notification,
            auto_ack=False  # We handle acknowledgments manually
        )
        
        channel.basic_consume(
            queue=USER_DATA_QUEUE_NAME,
            on_message_callback=send_user_personal_data,
            auto_ack=False  # We handle acknowledgments manually
        )
          
        channel.start_consuming()

    except KeyboardInterrupt:
        logger.info("Consumer interrupted. Shutting down...")
        if 'connection' in locals():
            connection.close()
    except Exception as e:
        logger.error(f"Error in RabbitMQ consumer: {e}")

# Call the consume_message function (not indented)
consume_message()
