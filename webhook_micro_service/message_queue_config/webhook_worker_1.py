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
