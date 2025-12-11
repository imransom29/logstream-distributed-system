from node import Node
from config import Config

if __name__ == "__main__":
    payment_node = Node(
        service_name="PaymentService",
        kafka_bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
    )
    payment_node.start_heartbeat()
    payment_node.start_log_generation()