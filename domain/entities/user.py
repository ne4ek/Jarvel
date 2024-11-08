from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import json

@dataclass
class User:
    user_id: Optional[int] = field(default=None)
    username: Optional[str] = field(default=None)
    full_name: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    personal_link: Optional[str] = field(default=None)
    arbitrary_data: Optional[str] = field(default=None)
    created_at: Optional[datetime] = field(default=None)

    first_name: Optional[str] = field(default=None)
    last_name: Optional[str] = field(default=None)

    _full_name: Optional[str] = field(default=None, init=False)
    _arbitrary_data: Optional[str] = field(default=None, init=False)

    @property
    def full_name(self) -> Optional[str]:
        return f"{self.first_name} {self.last_name}"
    
    @full_name.setter
    def full_name(self, value: Optional[str]):
        self._full_name = value

    @property
    def arbitrary_data(self) -> str:
        data = {
            "Имя и фамилия": f"{self.first_name} {self.last_name}",
            "Почта": self.email,
            "Телеграм": self.username,
            "Номер телефона": None,
            "Персональная ссылка": None,
            "Город проживания": None,
        }

        return json.dumps(data, ensure_ascii=False)

    @arbitrary_data.setter
    def arbitrary_data(self, value: Optional[str]):
        self._arbitrary_data = value