from node import Node
from config import Config

if __name__ == "__main__":
    order_node = Node(
        service_name="OrderService",
        kafka_bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
    )
    order_node.start_heartbeat()
    order_node.start_log_generation()