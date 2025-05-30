"""
common module
"""
from .languagemodels.openai import OpenAILLM


UPDATE_GRAPH_PROMPT = """
You are an AI expert specializing in graph memory management and optimization. Your task is to analyze existing graph memories alongside new information, and update the relationships in the memory list to ensure the most accurate, current, and coherent representation of knowledge.

Input:
1. Existing Graph Memories: A list of current graph memories, each containing source, target, and relationship information.
2. New Graph Memory: Fresh information to be integrated into the existing graph structure.

Guidelines:
1. Identification: Use the source and target as primary identifiers when matching existing memories with new information.
2. Conflict Resolution:
   - If new information contradicts an existing memory:
     a) For matching source and target but differing content, update the relationship of the existing memory.
     b) If the new memory provides more recent or accurate information, update the existing memory accordingly.
3. Comprehensive Review: Thoroughly examine each existing graph memory against the new information, updating relationships as necessary. Multiple updates may be required.
4. Consistency: Maintain a uniform and clear style across all memories. Each entry should be concise yet comprehensive.
5. Semantic Coherence: Ensure that updates maintain or improve the overall semantic structure of the graph.
6. Temporal Awareness: If timestamps are available, consider the recency of information when making updates.
7. Relationship Refinement: Look for opportunities to refine relationship descriptions for greater precision or clarity.
8. Redundancy Elimination: Identify and merge any redundant or highly similar relationships that may result from the update.

Task Details:
- Existing Graph Memories:
{existing_memories}

- New Graph Memory: {memory}

Output:
Provide a list of update instructions, each specifying the source, target, and the new relationship to be set. Only include memories that require updates.
"""

EXTRACT_ENTITIES_PROMPT = """
You are an advanced algorithm designed to extract structured information from text to construct knowledge graphs. Your goal is to capture comprehensive information while maintaining accuracy. Follow these key principles:

1. Extract only explicitly stated information from the text.
2. Identify nodes (entities/concepts), their types, and relationships.
3. Use "USER_ID" as the source node for any self-references (I, me, my, etc.) in user messages.

Nodes and Types:
- Aim for simplicity and clarity in node representation.
- Use basic, general types for node labels (e.g. "person" instead of "mathematician").

Relationships:
- Use consistent, general, and timeless relationship types.
- Example: Prefer "PROFESSOR" over "BECAME_PROFESSOR".

Entity Consistency:
- Use the most complete identifier for entities mentioned multiple times.
- Example: Always use "John Doe" instead of variations like "Joe" or pronouns.

Strive for a coherent, easily understandable knowledge graph by maintaining consistency in entity references and relationship types.

Adhere strictly to these guidelines to ensure high-quality knowledge graph extraction."""


def get_update_memory_prompt(existing_memories, memory, template):
    return template.format(existing_memories=existing_memories, memory=memory)


def get_update_memory_messages(existing_memories, memory):
    return [
        {
            "role": "user",
            "content": get_update_memory_prompt(
                existing_memories, memory, UPDATE_GRAPH_PROMPT
            ),
        },
    ]


def get_search_results(entities, query):
    search_graph_prompt = f"""\
You are an expert at searching through graph entity memories.
When provided with existing graph entities and a query, your task is to search through the provided graph entities to find the most relevant information from the graph entities related to the query.
The output should be from the graph entities only.

Here are the details of the task:
- Existing Graph Entities (source -> relationship -> target):
{entities}

- Query: {query}

The output should be from the graph entities only.
The output should be in the following JSON format:
{{
    "search_results": [
        {{
            "source_node": "source_node",
            "relationship": "relationship",
            "target_node": "target_node"
        }}
    ]
}}
"""

    messages = [
        {
            "role": "user",
            "content": search_graph_prompt,
        }
    ]

    llm = OpenAILLM()

    results = llm.generate_response(
        messages=messages, response_format={"type": "json_object"}
    )

    return results


def only_once(func):
    """Decorator to ensure a function is executed only once.

    On the first invokation, the function is executed normally.
    On subsequent calls, the cached result is returned.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with the only-once behavior.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if the function has already been executed
        if not wrapper.runnable:
            wrapper.output = func(*args, **kwargs)
            wrapper.runnable = True  # Mark function as having been executed
        return wrapper.output

    wrapper.runnable = False  # Initially mark the function as not executed
    wrapper.output = None  # Placeholder for the function output
    return wrapper
