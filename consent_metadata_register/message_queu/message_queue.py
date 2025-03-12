from abc import ABC, abstractmethod

class MessageQueue(ABC):
    @abstractmethod
    def publish_message(self, queue_name: str, message: dict) -> None:
        pass

