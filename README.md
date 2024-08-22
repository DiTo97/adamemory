# 🧠 adamemory

The adaptive memory layer for agentic AI — like mem0ai but inspired by human cognitive processes.

## overview

**adamemory** is a package that implements a dual-memory system combining **short-term memory (STM)** and **long-term memory (LTM)** to efficiently store, retrieve, and consolidate information over time. The architecture mimics natural memory processes, including the decay of unused memories and the consolidation of important information from short-term to long-term storage keeping the layer flexible and bounded over long-horizon trajectories.

The package is ideal for developers and researchers building intelligent systems that require adaptive memory management, such as conversational agents, autonomous systems, or cognitive simulations.

## installation

```bash
python -m pip install adamemory
```

## features

- **⚡ short-term memory (STM)**:
  - fast access to recent memories;
  - automatic clearing after consolidation;
  - caching mechanism relative to the slower LTM.

- **💾 long-term memory (LTM)**:
  - persistent storage of memories with decay over time;
  - recency-weighted nodes and edges prioritizing frequently accessed memories;
  - pruning mechanism to remove outdated or irrelevant information;
  - bounded over long-horizon trajectories while ensuring memory efficacy.

- **🔄 memory consolidation**:
  - periodic background consolidation of STM into LTM;
  - weight adjustment mechanism during consolidation to simulate memory strengthening;
  - decay of recency weights for memories not accessed during the consolidation cycle.

- **🕸️ hybrid storage**:
  - both STM and LTM are implemented using a graph structure;
  - nodes and edges are semantically enriched with contextual embeddings.

## usage

```python
```

## contributing

contributions to **adamemory** are welcome!

feel free to submit pull requests or open issues on our repository.

```bash
git clone https://github.com/DiTo97/adamemory.git && cd adamemory
```

```bash
python -m pip install poetry
```

```bash
poetry install
```

```bash
poetry shell
```

```bash
poetry run pre-commit install
```

## 🚀 roadmap

- **telemetry**: metrics and usage statistics;
- **hierarchical architecture**: community memories for weakly connected components (WCC);
- **memory consolidation enhancements**: improving efficiency and scalability of long-term memory mechanisms and storage;
- **multi-modal memory**: audio, text and vision all at once;
- **advanced cognitive architecture**: more sophisticated architectures that incorporate emotional and contextual factors into memory processes.

## license

see the [LICENSE](LICENSE) file for more details.
