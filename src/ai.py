import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ChatMessage
from pydantic import BaseModel, SecretStr, Field, field_validator


# ------------------------------------------- #


load_dotenv()


def normalize_name(name: str) -> str:
    return name.lower().strip().replace(" ", "_").replace("-", "_")


class OcelAttribute(BaseModel):
    name: str
    description: str

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_name(value)

class OcelObject(BaseModel):
    name: str
    description: str = Field(description="Reason or use this object has in the process. Should only have single responsibility or use.")
    attributes: list[OcelAttribute] = Field(default_factory=list)

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_name(value)

class OcelEvent(BaseModel):
    name: str
    description: str = Field(description="Reason or use this event has in the process. Should only have single responsibility or use.")
    attributes: list[OcelAttribute] = Field(default_factory=list)

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_name(value)

class OcelRelation(BaseModel):
    a: str
    b: str
    description: str

    @field_validator("a", mode="after")
    @classmethod
    def normalize_a(cls, value: str) -> str:
        return normalize_name(value)    

    @field_validator("b", mode="after")
    @classmethod
    def normalize_b(cls, value: str) -> str:
        return normalize_name(value)

class OcelEntity(BaseModel):
    objs: list[OcelObject] = Field(default_factory=list)
    evts: list[OcelEvent] = Field(default_factory=list)
    o2o: list[OcelRelation] = Field(default_factory=list)
    o2e: list[OcelRelation] = Field(default_factory=list)

Entity = OcelObject | OcelEvent | OcelRelation


class AiWorker:
    def __init__(self, model_name: str, structured_output: type):
        model_name = model_name.upper().replace("-", "_").replace(" ", "_")

        constructor = ChatOpenAI if "GPT" in model_name else ChatAnthropic

        model_options = {
            "GPT_5.5": {
                "model": os.getenv(f"{model_name}_MODEL_NAME"),
                "api_key": SecretStr(os.getenv(f"{model_name}_API_KEY")),
                "base_url": os.getenv(f"{model_name}_BASE_URL"),
                "stream_usage": False,
            },
            "CLAUDE_OPUS_4_6": {
                "model": os.getenv(f"{model_name}_MODEL_NAME"),
                "api_key": SecretStr(os.getenv(f"{model_name}_API_KEY")),
                "base_url": os.getenv(f"{model_name}_BASE_URL"),
                "stream_usage": False,
            },
            "GPT_5_NANO": {
                "model": os.getenv(f"{model_name}_MODEL_NAME"),
                "api_key": SecretStr(os.getenv(f"{model_name}_API_KEY")),
                "base_url": os.getenv(f"{model_name}_BASE_URL"),
                "stream_usage": False,
            },
            "CLAUDE_HAIKU_4_5": {
                "model": os.getenv(f"{model_name}_MODEL_NAME"),
                "api_key": SecretStr(os.getenv(f"{model_name}_API_KEY")),
                "base_url": os.getenv(f"{model_name}_BASE_URL"),
                "stream_usage": False,
            }
        }
        
        method = "json_schema" if "CLAUDE" in model_name else "function_calling"
        self.client = constructor(**model_options[model_name]).with_structured_output(structured_output, method=method, include_raw=True)
        return None
    
    def invoke(self, messages: list[ChatMessage], show_token_usage: bool = False) -> str:
        response = self.client.invoke(messages)
        if show_token_usage:
            print(response["raw"].usage_metadata)
        return response["parsed"]

