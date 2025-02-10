from dataclasses import dataclass, field
from typing import Optional
@dataclass
class TunnelingMessage:
    tunneling_id: Optional[int] = field(default=None)
    specify_chat_pinned_message_id: Optional[int] = field(default=None)
    source_chat_pinned_message_id: Optional[int] = field(default=None)
    to_chat_id: Optional[int] = field(default=None)
    to_topic_id: Optional[int] = field(default=None)
    from_chat_id: Optional[int] = field(default=None)
    from_topic_id: Optional[int] = field(default=None)