from pydantic import BaseModel


class QuestGenerateRequest(BaseModel):
    session_id: str


class QuestCompleteRequest(BaseModel):
    quest_id: int


class QuestItem(BaseModel):
    id: int
    session_id: str
    quest_text: str
    status: str
    generated_at: str

    model_config = {"from_attributes": True}


class QuestResponse(BaseModel):
    quest: str
