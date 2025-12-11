from kafka_utils import KafkaWrapper
import logging
from colorama import Fore, Style, Back, init
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import threading
import time

init(autoreset=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeTracker:
    def __init__(self, heartbeat_timeout=10):
        self.nodes = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.tracking_lock = threading.Lock()
        # Start a thread to check node status periodically
        threading.Thread(target=self.check_node_status, daemon=True).start()

    def display_alert(self, message, is_registration=True):
        """Display a prominent, distinguishable alert"""
        border = "=" * 50
        alert_color = Back.GREEN if is_registration else Back.RED
        text_color = Fore.BLACK

        print(f"\n{alert_color}{text_color}{border}{Style.RESET_ALL}")
        print(f"{alert_color}{text_color}{'  ' + message + '  ':^50}{Style.RESET_ALL}")
        print(f"{alert_color}{text_color}{border}{Style.RESET_ALL}\n")

    def update_heartbeat(self, message):
        with self.tracking_lock:
            node_id = message.get('node_id', 'Unknown')
            service_name = message.get('service_name', 'Unknown')
            timestamp = datetime.fromisoformat(message.get('timestamp', datetime.now().isoformat()))
            status = message.get('status', 'UP')

            # If node is new, trigger registration alert
            if node_id not in self.nodes:
                self.display_alert(f"New Node Registered: {service_name} (Node ID: {node_id[:8]})", is_registration=True)

            # Update or add node information
            self.nodes[node_id] = {
                'service_name': service_name,
                'last_heartbeat': timestamp,
                'status': status
            }

    def check_node_status(self):
        while True:
            current_time = datetime.now()
            with self.tracking_lock:
                # Create a copy of nodes to avoid modification during iteration
                nodes_copy = self.nodes.copy()
                
                for node_id, node_info in nodes_copy.items():
                    last_heartbeat = node_info['last_heartbeat']
                    time_since_last_heartbeat = current_time - last_heartbeat

                    # Check if node has been silent for too long
                    if time_since_last_heartbeat > timedelta(seconds=self.heartbeat_timeout):
                        if node_info['status'] == 'UP':
                            # Node just went down
                            self.display_alert(f"Node Disconnected: {node_info['service_name']} (Node ID: {node_id[:8]})", is_registration=False)
                            self.nodes[node_id]['status'] = 'DOWN'

            # Check every 5 seconds
            time.sleep(3)

class LogConsumer:
    def __init__(self, es_host='localhost', es_port=9200):
        self.kafka = KafkaWrapper(bootstrap_servers='192.168.222.127:9092')  #present current id
        self.es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])
        
        # Node tracker for monitoring registrations and disconnections
        self.node_tracker = NodeTracker()

        # Ensure the Elasticsearch index exists
        self.log_index = "microservice_logs"
        if not self.es.indices.exists(index=self.log_index):
            self.es.indices.create(index=self.log_index)
            logger.info(f"Created Elasticsearch index: {self.log_index}")

    def format_timestamp(self, timestamp_str):
        """Format ISO timestamp to a more readable format"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str

    def store_log(self, message):
        """Store log message in Elasticsearch"""
        try:
            self.es.index(index=self.log_index, document=message)
            logger.info(f"Log stored in Elasticsearch: {message}")
        except Exception as e:
            logger.error(f"Failed to store log in Elasticsearch: {e}")

    def handle_log(self, message):
        """Handle incoming log messages"""
        log_level = message.get('log_level', 'UNKNOWN')
        color = {
            'INFO': Fore.GREEN,
            'WARN': Fore.YELLOW,
            'ERROR': Fore.RED
        }.get(log_level, Fore.WHITE)
        
        timestamp = self.format_timestamp(message.get('timestamp', ''))
        service_name = message.get('service_name', 'Unknown')
        node_id = message.get('node_id', 'Unknown')[:8]
        msg = message.get('message', '')

        # Store log in Elasticsearch
        self.store_log(message)

        # Add extra details for WARN and ERROR logs
        extra_info = ""
        if log_level == 'WARN':
            response_time = message.get('response_time_ms', '')
            threshold = message.get('threshold_limit_ms', '')
            if response_time and threshold:
                extra_info = f" [Response: {response_time}ms, Threshold: {threshold}ms]"
        elif log_level == 'ERROR':
            error_details = message.get('error_details', {})
            if error_details:
                error_code = error_details.get('error_code', '')
                error_msg = error_details.get('error_message', '')
                extra_info = f" [Code: {error_code}, Details: {error_msg}]"

        print(f"{color}[{timestamp}] [{log_level}] {service_name} ({node_id}): {msg}{extra_info}{Style.RESET_ALL}")

    def handle_heartbeat(self, message):
        """Handle incoming heartbeat messages"""
        # Update node tracker
        self.node_tracker.update_heartbeat(message)

        timestamp = self.format_timestamp(message.get('timestamp', ''))
        service_name = message.get('service_name', 'Unknown')
        node_id = message.get('node_id', 'Unknown')[:8]
        status = message.get('status', 'UNKNOWN')
    
        color = Fore.GREEN if status == 'UP' else Fore.RED
        print(f"{color}[{timestamp}] [HEARTBEAT] {service_name} ({node_id}): Status: {status}{Style.RESET_ALL}")
       
    def handle_registration(self, message):
        """Handle incoming registration messages"""
        # Update node tracker
        self.node_tracker.update_heartbeat(message)

        timestamp = self.format_timestamp(message.get('timestamp', ''))
        service_name = message.get('service_name', 'Unknown')
        node_id = message.get('node_id', 'Unknown')[:8]
    
        print(f"{Fore.MAGENTA}[{timestamp}] [REGISTRATION] New service registered: {service_name} ({node_id}){Style.RESET_ALL}")

    def start(self):
        """Start consuming messages from all topics"""
        self.kafka.start_consumer('microservice_logs', self.handle_log, 'log-consumer')
        self.kafka.start_consumer('microservice_heartbeats', self.handle_heartbeat, 'heartbeat-consumer')
        self.kafka.start_consumer('microservice_registration', self.handle_registration, 'registration-consumer')

        logger.info("Started consuming messages from all topics")
        
        # Keep the main thread running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Shutting down consumers...")
            self.kafka.close()

if __name__ == "__main__":
    consumer = LogConsumer()
    consumer.start()
