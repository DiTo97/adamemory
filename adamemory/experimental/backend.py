import threading
import time
from typing import Any, Dict, List
from neo4j import GraphDatabase

class Neo4jGraph:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database=database)

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.data()

    def add_node(self, label: str, properties: Dict[str, Any]):
        query = f"CREATE (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])} }}) RETURN n"
        return self.execute_query(query, properties)

    def add_edge(self, start_node_label: str, start_node_id: Any, end_node_label: str, end_node_id: Any, relationship_type: str, weight: float = 1.0):
        query = (
            f"MATCH (a:{start_node_label}), (b:{end_node_label}) "
            f"WHERE ID(a) = $start_node_id AND ID(b) = $end_node_id "
            f"CREATE (a)-[r:{relationship_type} {{ weight: $weight }}]->(b) "
            f"RETURN r"
        )
        parameters = {
            "start_node_id": start_node_id,
            "end_node_id": end_node_id,
            "weight": weight
        }
        return self.execute_query(query, parameters)

    def search_nodes(self, label: str, properties: Dict[str, Any], user_id: str):
        query = f"MATCH (n:{label} {{ {', '.join([f'{k}: ${k}' for k in properties.keys()])}, user_id: $user_id }}) RETURN n"
        parameters = {**properties, "user_id": user_id}
        return self.execute_query(query, parameters)

    def update_node_property(self, label: str, node_id: Any, properties: Dict[str, Any]):
        query = f"MATCH (n:{label}) WHERE ID(n) = $node_id SET {', '.join([f'n.{k} = ${k}' for k in properties.keys()])} RETURN n"
        parameters = {"node_id": node_id, **properties}
        return self.execute_query(query, parameters)

    def delete_node(self, label: str, node_id: Any):
        query = f"MATCH (n:{label}) WHERE ID(n) = $node_id DETACH DELETE n"
        return self.execute_query(query, {"node_id": node_id})

    def prune_edges(self, weight_threshold: float):
        query = (
            f"MATCH ()-[r]->() "
            f"WHERE r.weight < $weight_threshold "
            f"DELETE r"
        )
        self.execute_query(query, {"weight_threshold": weight_threshold})

    def delete_orphan_nodes(self):
        query = (
            f"MATCH (n) "
            f"WHERE NOT (n)--() "
            f"DELETE n"
        )
        self.execute_query(query)

    def decrement_weights(self, user_id: str, decay_rate: float = 0.9):
        query = (
            f"MATCH (n {{ user_id: $user_id }}) "
            f"SET n.recency_weight = n.recency_weight * $decay_rate "
            f"RETURN n"
        )
        self.execute_query(query, {"user_id": user_id, "decay_rate": decay_rate})
