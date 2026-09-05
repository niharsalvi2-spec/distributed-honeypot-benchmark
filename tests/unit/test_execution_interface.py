import pytest
from infrastructure.nodes.node_interface import Node
from infrastructure.execution.native.native_node import NativeNode
from infrastructure.execution.docker.docker_node import DockerNode

def test_native_node_implements_interface():
    node = NativeNode(node_id="test_node_01", service="ssh", port=2222)
    assert isinstance(node, Node)
    assert node.start() is True
    health = node.health_check()
    assert health["node_id"] == "test_node_01"
    assert health["status"] == "HEALTHY"
    assert health["execution_mode"] == "native"
    metrics = node.get_metrics()
    assert "cpu_percent" in metrics
    assert node.stop() is True

def test_docker_node_implements_interface():
    node = DockerNode(node_id="test_docker_01", service="http", port=8080, container_name="test_canary")
    assert isinstance(node, Node)
    assert node.execution_mode == "docker"
    health = node.health_check()
    assert health["node_id"] == "test_docker_01"
    assert health["execution_mode"] == "docker"
