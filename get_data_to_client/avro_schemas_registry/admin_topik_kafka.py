from confluent_kafka.admin import AdminClient, NewTopic

class KafkaAdmin:
    def __init__(self, bootstrap_servers):
        # Initialize the Kafka AdminClient with the provided broker(s)
        self.admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    def get_all_topics(self):
        # Fetch metadata to retrieve topics
        try:
            metadata = self.admin_client.list_topics(timeout=10)
            topics = metadata.topics
            return list(topics.keys())  # Return all topic names
        except Exception as e:
            print(f"Failed to retrieve topics: {e}")
            return []
            
    def topic_exists(self, topic_name):
        """Check if a specific topic already exists in Kafka."""
        existing_topics = self.get_all_topics()
        return topic_name in existing_topics
        
    def create_topic(self, topic_name, num_partitions=1, replication_factor=1):
        """
        Create a new topic in Kafka if it doesn't exist.
        
        :param topic_name: Name of the topic to create.
        :param num_partitions: Number of partitions for the topic.
        :param replication_factor: Replication factor for the topic.
        :return: Success message or error.
        """
        # Check if the topic already exists
        if self.topic_exists(topic_name):
            print(f"Topic '{topic_name}' already exists.")
            return
        
        # Define the new topic to create
        new_topic = NewTopic(topic=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)

        # Try to create the new topic
        try:
            result = self.admin_client.create_topics([new_topic])
            # Wait for the result of topic creation
            result[topic_name].result()  # This will raise an exception if topic creation fails
            print(f"Topic '{topic_name}' successfully created.")
        except Exception as e:
            print(f"Failed to create topic '{topic_name}': {e}")

# Example usage
if __name__ == "__main__":
    kafka_admin = KafkaAdmin(bootstrap_servers="localhost:9092")
    
    # Get all Kafka topics
    topics = kafka_admin.get_all_topics()
    
    if topics:
        print(f"Available Topics: {topics}")
    else:
        print("No topics found or unable to fetch topics.")

