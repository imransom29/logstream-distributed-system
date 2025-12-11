from node import Node
from config import Config

if __name__ == "__main__":
    inventory_node = Node(
        service_name="InventoryService",
        kafka_bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS
    )
    inventory_node.start_heartbeat()
    inventory_node.start_log_generation()