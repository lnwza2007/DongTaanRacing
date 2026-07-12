from typing import Dict, Any
from decoders.base import BaseDecoder
from config.channels import CHANNELS_BY_ID
from config.can_ids import M150_PRIMARY, M150_SECONDARY, M150_FUEL_LAMBDA, M150_GEAR_SPEED

class M150Decoder(BaseDecoder):
    def __init__(self):
        # Cache list of decodable channels by their target CAN IDs
        self.supported_ids = {M150_PRIMARY, M150_SECONDARY, M150_FUEL_LAMBDA, M150_GEAR_SPEED}

    def decode(self, msg_id: int, data: bytes) -> Dict[str, Any]:
        decoded_data = {}
        if msg_id not in self.supported_ids:
            return decoded_data

        channels = CHANNELS_BY_ID.get(msg_id, [])
        for ch in channels:
            # Bounds check
            if ch.byte_offset + ch.byte_length > len(data):
                continue
            
            raw_bytes = data[ch.byte_offset : ch.byte_offset + ch.byte_length]
            
            # Unpack bytes
            raw_val = int.from_bytes(
                raw_bytes,
                byteorder=ch.byte_order,
                signed=ch.signed
            )
            
            # Apply scaling formula: physical_val = raw_val * multiplier + offset
            physical_val = (raw_val * ch.multiplier) + ch.offset
            
            # Format float decimals for readability
            if isinstance(physical_val, float):
                physical_val = round(physical_val, 4)
                
            decoded_data[ch.name] = physical_val
            
        return decoded_data
