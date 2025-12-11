import uuid
import time
import threading
import random
import json
from datetime import datetime
from colorama import Fore, Style, init
from threading import Lock
from fluent import sender
from kafka_utils import KafkaWrapper
from config import Config

init(autoreset=True)
print_lock = Lock()

class Node:
    message_colors = {
        "registration": Fore.CYAN,
        "heartbeat": Fore.RED,
        "Log": Fore.GREEN
    }
    key_color = Fore.LIGHTMAGENTA_EX
    value_color = Fore.LIGHTYELLOW_EX

    def __init__(self, service_name, kafka_bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS):
        self.node_id = str(uuid.uuid4())
        self.service_name = service_name
        self.status = "UP"
        
        # Initialize Fluentd sender
        self.fluent_sender = sender.FluentSender(
            'microservice',
            host=Config.FLUENTD_HOST,
            port=Config.FLUENTD_PORT
        )
        
        # Initialize Kafka wrapper
        self.kafka = KafkaWrapper(bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS)
        self.registered=False
        self.register_node()
    
    def format_message(self, message):
        """
        Format JSON message to color keys and values distinctly.
        """
        formatted_message = ""
        for key, value in message.items():
            formatted_message += f"{Node.key_color}{key}{Style.RESET_ALL}: {Node.value_color}{value}{Style.RESET_ALL}, "
        return "{" + formatted_message.rstrip(", ") + "}"

    def print_message(self, message_type, message_content):
        with print_lock:
            color = Node.message_colors[message_type]
            formatted_content = self.format_message(json.loads(message_content))
            print(color + f"{message_type.capitalize()}:" + Style.RESET_ALL, formatted_content)
    
    def send_to_fluentd(self, tag, message):
        """Send message to Fluentd"""
        try:
            self.fluent_sender.emit(tag, message)
        except Exception as e:
            print(f"Error sending to Fluentd: {e}")

    def send_to_kafka(self, topic, message):
        """Send message to Kafka"""
        try:
            self.kafka.send_message(topic, message)
        except Exception as e:
            print(f"Error sending to Kafka: {e}")
    
    def register_node(self):
        if not self.registered:
            registration_message = {
                "node_id": self.node_id,
                "message_type": "registration",
                "service_name": self.service_name,
                "timestamp": datetime.now().isoformat()
            }
            self.print_message("registration", json.dumps(registration_message))
            self.send_to_kafka('microservice_registration', registration_message)
            self.registered = True

    
    def generate_log(self, log_level, message, extra_data=None):
        log_message = {
            "log_id": str(uuid.uuid4()),
            "node_id": self.node_id,
            "log_level": log_level,
            "message_type": "LOG",
            "message": message,
            "service_name": self.service_name,
            "timestamp": datetime.now().isoformat()
        }
        if extra_data:
            log_message.update(extra_data)
            
        # Send to both console and message brokers
        self.print_message("Log", json.dumps(log_message))
        self.send_to_fluentd(f'log.{log_level.lower()}', log_message)
        self.send_to_kafka('microservice_logs', log_message)

    def send_heartbeat(self):
        heartbeat_message = {
            "node_id": self.node_id,
            "message_type": "HEARTBEAT",
            "service_name": self.service_name,  # Added service_name
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to both console and message brokers
        self.print_message("heartbeat", json.dumps(heartbeat_message))
        self.send_to_fluentd('heartbeat', heartbeat_message)
        self.send_to_kafka('microservice_heartbeats', heartbeat_message)

    def start_heartbeat(self, interval=5):
        def heartbeat():
            while self.status == "UP":
                self.send_heartbeat()
                time.sleep(interval)
        threading.Thread(target=heartbeat).start()
    
    def start_log_generation(self, interval=3):
        def generate_logs():
            log_levels = ["INFO", "WARN", "ERROR"]
            while self.status == "UP":
                log_level = random.choice(log_levels)
                if log_level == "INFO":
                    self.generate_log("INFO", "This is an info log.")
                elif log_level == "WARN":
                    self.generate_log("WARN", "This is a warning log.", {
                        "response_time_ms": random.randint(100, 500),
                        "threshold_limit_ms": 300
                    })
                elif log_level == "ERROR":
                    self.generate_log("ERROR", "This is an error log.", {
                        "error_details": {
                            "error_code": "500",
                            "error_message": "Internal Server Error"
                        }
                    })
                time.sleep(interval)
        threading.Thread(target=generate_logs).start()

    def __del__(self):
        if hasattr(self, 'fluent_sender'):
            self.fluent_sender.close()
        if hasattr(self, 'kafka'):
            self.kafka.close()