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
    tunnel_type: Optional[str] = field(default='one_way')
    is_active: Optional[bool] = field(default=True)
    company_id: Optional[int] = field(default=None)
    user_id: Optional[int] = field(default=None)