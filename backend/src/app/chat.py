from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4100)

    @field_validator("content")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A mensagem não pode estar vazia.")
        return value


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def require_user_turn(self) -> "ChatRequest":
        if any(
            message.role == "user" and len(message.content) > 4000
            for message in self.messages
        ):
            raise ValueError("A mensagem do usuário excede 4000 caracteres.")
        if self.messages[-1].role != "user":
            raise ValueError("A última mensagem deve ser do usuário.")
        if sum(len(message.content) for message in self.messages) > 40000:
            raise ValueError("O histórico excede o limite desta demonstração.")
        return self


class ChatResponse(BaseModel):
    message: ChatMessage
    mode: Literal["echo"] = "echo"


def echo_reply(request: ChatRequest) -> ChatResponse:
    """Recebe o histórico completo; nesta fase apenas ecoa o turno atual."""
    return ChatResponse(
        message=ChatMessage(
            role="assistant", content=f"Você disse: {request.messages[-1].content}"
        )
    )
