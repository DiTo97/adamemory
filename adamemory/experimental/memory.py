import threading
import time
from typing import Any, Dict, List

from .storage import LTM, STM


class Memory:
    def __init__(self, config, consolidation_interval: int = 60 * 60 * 24):
        self.stm = STM(config)
        self.ltm = LTM(config)
        self.consolidation_interval = consolidation_interval
        self.consolidation_thread = threading.Thread(target=self._consolidation_loop)
        self.consolidation_thread.daemon = True
        self.consolidation_thread.start()

    def add_memory(self, data: Dict[str, Any]):
        self.stm.add_memory(data)

    def search_memory(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = self.stm.search_memory(query)
        if result:
            return result

        ltm_result = self.ltm.search_memory(query)
        if ltm_result:
            self.stm.add_memory(ltm_result)
            return ltm_result

        return None

    def consolidate(self):
        stm_memories = self.stm.get_all_memories()
        self.ltm.consolidate_memory(stm_memories)
        self.stm.clear()

    def prune(self):
        self.ltm._prune_graph()

    def _consolidation_loop(self):
        while True:
            time.sleep(self.consolidation_interval)
            self.consolidate()
