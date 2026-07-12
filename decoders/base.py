from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDecoder(ABC):
    @abstractmethod
    def decode(self, msg_id: int, data: bytes) -> Dict[str, Any]:
        """
        Decodes a CAN message payload.
        Returns a dict of channel_name -> physical_value.
        """
        pass
