from typing import Dict, Any, List

from .backend import Neo4jGraph

class STM:
    """short-term memory store"""
    def __init__(self, config):
        self.graph = Neo4jGraph(config.graph_store.config.url, config.graph_store.config.username, config.graph_store.config.password, "STM")
        self.user_id = config.user_id  # Assume user_id is passed in the configuration

    def add_memory(self, data: Dict[str, Any]):
        node = self.graph.add_node(data['label'], {**data['properties'], 'user_id': self.user_id})
        if 'relations' in data:
            for relation in data['relations']:
                self.graph.add_edge(
                    data['label'], node['n'].id,
                    relation['label'], relation['id'],
                    relation['type']
                )

    def search_memory(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.graph.search_nodes(query['label'], query['properties'], self.user_id)

    def get_all_memories(self) -> List[Dict[str, Any]]:
        query = "MATCH (n { user_id: $user_id }) RETURN n"
        return self.graph.execute_query(query, {"user_id": self.user_id})

    def clear(self):
        query = "MATCH (n { user_id: $user_id }) DETACH DELETE n"
        self.graph.execute_query(query, {"user_id": self.user_id})


class LTM:
    """long-term memory store"""
    def __init__(self, config):
        self.graph = Neo4jGraph(config.graph_store.config.url, config.graph_store.config.username, config.graph_store.config.password, "LTM")
        self.user_id = config.user_id  # Assume user_id is passed in the configuration

    def add_memory(self, data: Dict[str, Any]):
        node = self.graph.add_node(data['label'], {**data['properties'], 'recency_weight': 1.0, 'user_id': self.user_id})
        if 'relations' in data:
            for relation in data['relations']:
                self.graph.add_edge(
                    data['label'], node['n'].id,
                    relation['label'], relation['id'],
                    relation['type']
                )

    def search_memory(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.graph.search_nodes(query['label'], query['properties'], self.user_id)

    def consolidate_memory(self, stm_memories: List[Dict[str, Any]]):
        for memory in stm_memories:
            existing_nodes = self.graph.search_nodes(memory['label'], memory['properties'], self.user_id)
            if existing_nodes:
                # Update the existing node's recency weight and properties
                node_id = existing_nodes[0]['n'].id
                self.graph.update_node_property(memory['label'], node_id, {'recency_weight': existing_nodes[0]['n']['recency_weight'] + 1})
            else:
                # Add new memory to LTM
                self.add_memory(memory)

        # Decay weights for all nodes in the LTM
        self.graph.decrement_weights(self.user_id)

        # Prune the graph after consolidation
        self._prune_graph()

    def _prune_graph(self):
        weight_threshold = 0.5  # This threshold can be adjusted based on desired retention
        self.graph.prune_edges(weight_threshold)
        self.graph.delete_orphan_nodes()
