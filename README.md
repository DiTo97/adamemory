# 🧠 adamemory

The adaptive memory layer for agentic AI — like mem0ai but inspired by human cognitive processes.

## 🌟 Overview

**adamemory** is a package that implements a dual-memory system combining **short-term memory (STM)** and **long-term memory (LTM)** to efficiently store, retrieve, and consolidate information over time. The architecture mimics natural memory processes, including the decay of unused memories and the consolidation of important information from short-term to long-term storage, keeping the layer flexible and bounded over long-horizon trajectories.

The package is ideal for developers and researchers building intelligent systems that require adaptive memory management, such as conversational agents, autonomous systems, or cognitive simulations.

## ⚙️ Installation

To install **adamemory**, simply run:

```bash
python -m pip install adamemory
```

## ✨ Features

- **⚡ Short-Term Memory (STM)**:
  - Fast access to recent memories.
  - Automatic clearing after consolidation.
  - Caching mechanism relative to the slower LTM.

- **💾 Long-Term Memory (LTM)**:
  - Persistent storage of memories with decay over time.
  - Recency-weighted nodes and edges prioritizing frequently accessed memories.
  - Pruning mechanism to remove outdated or irrelevant information.
  - Bounded over long-horizon trajectories while ensuring memory efficacy.

- **🔄 Memory Consolidation**:
  - Periodic background consolidation of STM into LTM.
  - Weight adjustment mechanism during consolidation to simulate memory strengthening.
  - Decay of recency weights for memories not accessed during the consolidation cycle.

- **🕸️ Hybrid Storage**:
  - Both STM and LTM are implemented using a graph structure.
  - Nodes and edges are semantically enriched with contextual embeddings.

## 🚀 Usage

```python
# Example usage code will go here
```

## 🤝 Contributing

Contributions to **adamemory** are welcome! Feel free to submit pull requests or open issues on our repository.

Clone the repository and set up the development environment:

```bash
git clone https://github.com/DiTo97/adamemory.git && cd adamemory
```

Install development dependencies using ``poetry``:

```bash
python -m pip install poetry
poetry install
poetry shell
poetry run pre-commit install
```

## 🛠️ Roadmap

- **📊 Telemetry**: Metrics and usage statistics.
- **🏗️ Hierarchical Architecture**: Community memories for weakly connected components (WCC).
- **🛠️ Memory Consolidation Enhancements**: Improving efficiency and scalability of long-term memory mechanisms and storage.
- **🎨 Multi-Modal Memory**: Audio, text, and vision all at once.
- **🧠 Advanced Cognitive Architecture**: More sophisticated architectures that incorporate emotional and contextual factors into memory processes.

## 📈 Telemetry Information

We collect anonymous usage metrics to enhance our package's quality and user experience. This includes data like feature usage frequency and system information, but never personal details. The data helps us prioritize improvements and ensure compatibility. If you wish to opt-out, set the environment variable ``ADAMEMORY_TELEMETRY_ENABLED=false``. For more information on how to disable telemetry, please refer to the documentation [here](adamemory/telemetry.py). We prioritize data security and do not share this data externally.

## 📄 License

See the [LICENSE](LICENSE) file for licensing information.
