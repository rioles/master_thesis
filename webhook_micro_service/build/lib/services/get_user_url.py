import hmac
import hashlib
import os
import time
from datetime import datetime
from models import storage
from dotenv import load_dotenv

load_dotenv()
my_app = Celery('webhook_handler', broker='amqp://guest@localhost:5672//', backend='rpc://')

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

class GenerateWebhookSignature:
    def __init__(self, client_secret, data):
        self.client_secret = client_secret
        self.data = data
        self.message_que = message_que
        
    def generate_webhook_header(self):
    	timestamp = str(int(time.time()))
    	message = f"{data}{timestamp}"
    	signature = hmac.new(client_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    	return {"Content-Type": "application/json","X-Signature":signature,"X-Timestamp": timestamp}
    	
	def send_message():
		message_queue = self.message_que
    	queue_name = data.get("queue_name", "default_queue")
    	message_queue.publish_message(queue_name, data)
    	return jsonify({"status": "Message sent successfully"}), 200

    	
    	
if __name__=="__main__":
	client_secret = os.getenv('CLIENT_SECRET')
	storage.set(client_secret, "rodolphebabao")
	#data = storage.get(client_secret)
	#generate_webhook = GenerateWebhookSignature(client_secret,data)
	#print(generate_webhook.generate_signature())
    	
    

    
