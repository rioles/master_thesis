from __future__ import absolute_import
from webhook_worker import process_data
from kombu import Consumer
from kombu.mixins import ConsumerMixin
from kombu import Connection, Exchange, Queue, Consumer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ configurations
rabbitmq_url = "amqp://guest:guest@localhost:5672//"
queue_name = "webhook_data"

# Kombu Exchange and Queue setup
exchange = Exchange('webhook_exchange', type='direct', durable=True)
queue = Queue(name=queue_name, exchange=exchange, routing_key=queue_name)



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kombu Exchange and Queue definitions
exchange = Exchange('webhook_exchange', 'topic', durable=True)
queue = Queue('webhook_data', exchange=exchange, routing_key='webhook.data.#')

# Task queue list (used by the consumer)
task_queues = [queue]

class Worker(ConsumerMixin):
    """
    Kombu ConsumerMixin-based worker to consume messages from RabbitMQ.
    """
    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        """
        Specify queues and callbacks for this consumer.
        """
        return [
            Consumer(
                queues=task_queues,
                callbacks=[self.process_task],
                accept=['json', 'pickle', 'msgpack', 'yaml']
            )
        ]

    def process_task(self, body, message):
        """
        Process a single message from the queue.
        """
        try:
            body_str = body.decode('utf-8')
            message = json.loads(body_str)
            logger.info("Received message: %s", body)

            # Trigger the Celery task asynchronously
            process_data(message[1])

            # Acknowledge the message after successful processing
            logger.info("Message processed and acknowledged.")
            message.ack()
        except Exception as e:
            logger.error("Error processing message: %s", str(e))
            message.reject()

def run_consumer():
    """
    Entry point for running the consumer.
    """
    logger.info("Connecting to RabbitMQ...")
    with Connection("amqp://localhost:5672//") as conn:
        logger.info("Connected to RabbitMQ. Waiting for tasks...")
        try:
            Worker(conn).run()
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user.")

if __name__ == "__main__":
    run_consumer()
