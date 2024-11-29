import pika
import json
import logging
from celery import Celery
from celery.utils.log import get_task_logger
from message_queue_config.message_queue import MessageQueue

# Initialize logger
logger = get_task_logger(__name__)

# Celery app configuration
appli = Celery('webhook_handler', broker='amqp://guest@localhost:5672//', backend='rpc://')

class RabbitMQ(MessageQueue):
    def __init__(self, celery_app, host='localhost'):
        self.host = host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host))
        self.channel = self.connection.channel()
        self.celery_app = celery_app

    def publish_message(self, task_name: str, queue_name: str, **kwargs) -> None:
        try:
            # Declare the queue to ensure it exists
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Send task to the specified queue
            r = self.celery_app.send_task(task_name, kwargs=kwargs, queue=queue_name)

            # Log the task ID
            logging.info("Task ID: %s", r.id)
            return r.id
        except Exception as e:
            # Log the error and handle it gracefully
            logging.error("An error occurred in send_data_to_rabbitmq: %s", str(e))
            return None
            

if __name__ == "__main__":
    message = {"payment_id": 123, "amount": 100}
    
    # Instantiate the RabbitMQ class with the Celery app
    r = RabbitMQ(appli)

    # Printing the Celery app and RabbitMQ instance
    print(appli)
    print(r)

    # Publish a message to the queue
    r.publish_message('try_app', "consent", **message)

    # Print the result of the publish_message method
    print(r.publish_message('try_app', "consent", **message))

