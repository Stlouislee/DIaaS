from typing import List, Dict, Any, Optional
from neo4j import AsyncDriver, AsyncSession

class GraphService:
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    def _get_dataset_label(self, dataset_id: str) -> str:
        return f"Graph_{dataset_id.replace('-', '_')}"

    async def create_node(self, dataset_id: str, label: str, properties: Dict[str, Any]):
        dataset_label = self._get_dataset_label(dataset_id)
        query = (
            f"CREATE (n:{dataset_label}:{label} $props) "
            "RETURN n"
        )
        async with self.driver.session() as session:
            result = await session.run(query, props=properties)
            record = await result.single()
            return dict(record["n"])

    async def create_relationship(self, dataset_id: str, from_node_id: int, to_node_id: int, rel_type: str, properties: Dict[str, Any]):
        dataset_label = self._get_dataset_label(dataset_id)
        query = (
            f"MATCH (a:{dataset_label}), (b:{dataset_label}) "
            "WHERE id(a) = $from_id AND id(b) = $to_id "
            f"CREATE (a)-[r:{rel_type} $props]->(b) "
            "RETURN r"
        )
        async with self.driver.session() as session:
            result = await session.run(query, from_id=from_node_id, to_id=to_node_id, props=properties)
            record = await result.single()
            if record:
                return dict(record["r"])
            return None

    async def get_nodes(self, dataset_id: str, label: Optional[str] = None, limit: int = 100):
        dataset_label = self._get_dataset_label(dataset_id)
        label_filter = f":{label}" if label else ""
        query = (
            f"MATCH (n:{dataset_label}{label_filter}) "
            "RETURN n, id(n) as node_id LIMIT $limit"
        )
        async with self.driver.session() as session:
            result = await session.run(query, limit=limit)
            nodes = []
            async for record in result:
                node_data = dict(record["n"])
                node_data["_id"] = record["node_id"]
                nodes.append(node_data)
            return nodes

    async def get_neighbors(self, dataset_id: str, node_id: int):
        dataset_label = self._get_dataset_label(dataset_id)
        query = (
            f"MATCH (n:{dataset_label})-[r]-(m:{dataset_label}) "
            "WHERE id(n) = $node_id "
            "RETURN m, r, type(r) as rel_type, id(m) as neighbor_id"
        )
        async with self.driver.session() as session:
            result = await session.run(query, node_id=node_id)
            neighbors = []
            async for record in result:
                neighbor = {
                    "node": dict(record["m"]), 
                    "node_id": record["neighbor_id"],
                    "relationship": dict(record["r"]),
                    "type": record["rel_type"]
                }
                neighbors.append(neighbor)
            return neighbors
    
    async def shortest_path(self, dataset_id: str, from_node_id: int, to_node_id: int):
        dataset_label = self._get_dataset_label(dataset_id)
        # Using simple shortestPath cypher
        query = (
            f"MATCH (a:{dataset_label}), (b:{dataset_label}), "
            f"p = shortestPath((a)-[*]-(b)) "
            "WHERE id(a) = $from_id AND id(b) = $to_id "
            "RETURN p"
        )
        async with self.driver.session() as session:
            result = await session.run(query, from_id=from_node_id, to_id=to_node_id)
            record = await result.single()
            if record:
                # Path object handling might need serialization logic for complex cases
                # Return simple length and nodes for now
                path = record["p"]
                return {
                    "length": len(path),
                    "nodes": [dict(n) for n in path.nodes],
                    "relationships": [dict(r) for r in path.relationships]
                }
            return None
