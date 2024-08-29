import json

from langchain_community.graphs import Neo4jGraph
from pydantic import BaseModel, Field

from .clients.openai import OpenAIClient
from .common import EXTRACT_ENTITIES_PROMPT, get_update_memory_messages
from .embeddings.openai import OpenAIEmbedding
from .languagemodels.openai import OpenAILLM
from .toolkit import ADD_MEMORY_TOOL_GRAPH, NOOP_TOOL, UPDATE_MEMORY_TOOL_GRAPH


client = OpenAIClient.get_instance()


class GraphData(BaseModel):
    source: str = Field(..., description="The source node of the relationship")
    target: str = Field(..., description="The target node of the relationship")
    relationship: str = Field(..., description="The type of the relationship")


class Entities(BaseModel):
    source_node: str
    source_type: str
    relation: str
    destination_node: str
    destination_type: str


class ADDQuery(BaseModel):
    entities: list[Entities]


class SEARCHQuery(BaseModel):
    nodes: list[str]
    relations: list[str]


def get_embedding(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


class Memory:
    def __init__(self, config):
        self.config = config
        self.graph = Neo4jGraph(
            config.graph_store.config.url,
            config.graph_store.config.username,
            config.graph_store.config.password,
        )
        self.llm = OpenAILLM()
        self.embedding_model = OpenAIEmbedding()
        self.user_id = None
        self.threshold = 0.7
        self.model_name = "gpt-4o-2024-08-06"

    def add(self, data):
        search_output = self._search(data)
        extracted_entities = (
            client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": EXTRACT_ENTITIES_PROMPT.replace(
                            "USER_ID", self.user_id
                        ),
                    },
                    {"role": "user", "content": data},
                ],
                response_format=ADDQuery,
                temperature=0,
            )
            .choices[0]
            .message.parsed.entities
        )

        update_memory_prompt = get_update_memory_messages(
            search_output, extracted_entities
        )
        tools = [UPDATE_MEMORY_TOOL_GRAPH, ADD_MEMORY_TOOL_GRAPH, NOOP_TOOL]

        memory_updates = (
            client.beta.chat.completions.parse(
                model=self.model_name,
                messages=update_memory_prompt,
                tools=tools,
                temperature=0,
            )
            .choices[0]
            .message.tool_calls
        )

        to_be_added = []
        for item in memory_updates:
            function_name = item.function.name
            arguments = json.loads(item.function.arguments)
            if function_name == "add_graph_memory":
                to_be_added.append(arguments)
            elif function_name == "update_graph_memory":
                self._update_relationship(
                    arguments["source"],
                    arguments["destination"],
                    arguments["relationship"],
                )
            elif function_name == "update_name":
                self._update_name(arguments["name"])
            elif function_name == "noop":
                continue

        for item in to_be_added:
            source = item["source"].lower().replace(" ", "_")
            source_type = item["source_type"].lower().replace(" ", "_")
            relation = item["relationship"].lower().replace(" ", "_")
            destination = item["destination"].lower().replace(" ", "_")
            destination_type = item["destination_type"].lower().replace(" ", "_")

            source_embedding = get_embedding(source)
            dest_embedding = get_embedding(destination)

            cypher = f"""
            MERGE (n:{source_type} {{name: $source_name}})
            ON CREATE SET n.created = timestamp(), n.embedding = $source_embedding
            MERGE (m:{destination_type} {{name: $dest_name}})
            ON CREATE SET m.created = timestamp(), m.embedding = $dest_embedding
            MERGE (n)-[r:{relation}]->(m)
            RETURN n, r, m
            """
            params = {
                "source_name": source,
                "dest_name": destination,
                "source_embedding": source_embedding,
                "dest_embedding": dest_embedding,
            }

            with self.graph.driver.session() as session:
                session.run(cypher, params)

        return "Done"

    def _update_relationship(self, source, destination, relationship):
        source_type = source.split("::")[0].lower()
        dest_type = destination.split("::")[0].lower()
        cypher = f"""
        MATCH (n:{source_type} {{name: $source}})-[r]->(m:{dest_type} {{name: $destination}})
        SET r.name = $relationship
        RETURN n, r, m
        """
        params = {
            "source": source,
            "destination": destination,
            "relationship": relationship,
        }
        with self.graph.driver.session() as session:
            session.run(cypher, params)

    def _search(self, data):
        return self.graph.query(data)

    def _update_name(self, name):
        self.user_id = name
