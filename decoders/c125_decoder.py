from typing import Dict, Any
from decoders.base import BaseDecoder
from config.channels import CHANNELS_BY_ID
from config.can_ids import C125_LAP_DATA

class C125Decoder(BaseDecoder):
    def __init__(self):
        self.supported_ids = {C125_LAP_DATA}

    def decode(self, msg_id: int, data: bytes) -> Dict[str, Any]:
        decoded_data = {}
        if msg_id not in self.supported_ids:
            return decoded_data

        channels = CHANNELS_BY_ID.get(msg_id, [])
        for ch in channels:
            if ch.byte_offset + ch.byte_length > len(data):
                continue
            
            raw_bytes = data[ch.byte_offset : ch.byte_offset + ch.byte_length]
            raw_val = int.from_bytes(
                raw_bytes,
                byteorder=ch.byte_order,
                signed=ch.signed
            )
            
            physical_val = (raw_val * ch.multiplier) + ch.offset
            
            if isinstance(physical_val, float):
                physical_val = round(physical_val, 4)
                
            decoded_data[ch.name] = physical_val
            
        return decoded_data
