"""
Node Failure Injection Simulator.
Simulates ungraceful termination and mid-session disconnection.
"""
from infrastructure.nodes.node_interface import Node

class NodeFailureSimulator:
    @staticmethod
    def kill_node(node: Node) -> bool:
        return node.stop()

    @staticmethod
    def restart_node(node: Node) -> bool:
        return node.start()
