from typing import Literal, Optional

from pydantic import BaseModel


class MessageAddSchema(BaseModel):
    message_id: int
    from_user_id: int
    chat_id: int
    text: str