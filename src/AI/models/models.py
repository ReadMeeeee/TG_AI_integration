from pydantic import BaseModel, Field


class Instruction(BaseModel):
    system_prompt: str = (
        Field(..., description="Текст инструкций"))
    response_format: str = (
        Field("text", description="Описание формата ответа"))
    context: str | None = None


class LLMRequest(BaseModel):
    instruction_block: Instruction
    task: str

    def to_messages(self) -> list[dict[str, str]]:
        content = (
            f"Контекст:\n{self.instruction_block.context or '-'}\n\n"
            f"Формат вывода:\n{self.instruction_block.response_format}\n\n"
            f"Входные данные:\n{self.task}"
        )
        return [
            {"role": "system", "content": self.instruction_block.system_prompt},
            {"role": "user", "content": content},
        ]


class LLMResponse(BaseModel):
    response_answer: str
    response_context: str | None = None
