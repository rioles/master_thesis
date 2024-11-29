import pika
import json
import logging
from celery import current_app
from celery import Celery
from celery.utils.log import get_task_logger
from message_queue_config.message_queue import MessageQueue  # Assuming correct import path
from message_queue_config.rabbitmq import RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
from models import storage

import json
import pika
from celery.utils.log import get_task_logger

# Initialize logger
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)
appli = Celery('webhook_handler', broker='amqp://guest@localhost:5672//', backend='rpc://')

logger.setLevel(logging.INFO)



connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
def send_webhook_data(ch, method, properties, body):
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
        r = appli.send_task('process_data', kwargs={'data': message}, queue='webhook_data')
        #process_data(message)
        # Acknowledge the message as processed
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON message: {e}")
        # Reject the message and requeue it for another attempt
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

@appli.task(name="webhook_handler")
def process_data(data):
    try:
        if data.get("validity") == False:  # Corrected condition
            validity_expire(data)
        else:
            send_to_kafka(data)
    except Exception as e:
        logger.error(f"Error in processing data: {e}")
        raise


def validity_expire(data):
    all_data = {"data": data}
    message = {
        "status": 204,
        "data": [],
        "message": "Consent date is expired"
    }
    all_data["message"] = message
    send_dat_to_webhook(all_data)
    
     
def send_to_kafka(data):
    all_data = {"data": data} 
    if "consent_grant" in data:
        try:
            logger.info(f"Sending data to Kafka: {data}")
            send_data_to_topic(data)
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {e}")
            raise
    else:
        send_dat_to_webhook(all_data)

     	
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
    except Exception as e:
        logger.error(f"Error in send_data_to_topic: {e}")
        raise        

def send_dat_to_webhook(all_data):
    try:
        client_id = all_data["data"]["client"]["client_id"]
        webhook_url = storage.get(client_id)
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
        logger.error(f"Error in send_dat_to_webhook: {e}")
        raise
		 
channel.queue_declare(queue="webhook_data", durable=True)
logger.info("Starting consumer.")
channel.basic_consume(queue="webhook_data", on_message_callback=send_webhook_data, auto_ack=True)
channel.start_consuming()
connection.close()

