from typing import TypedDict, Literal
from . import prompt_text

MessageMode = Literal["system"] | Literal["assistant"] | Literal["user"]
Message = TypedDict("MESSAGE", {"role": str, "type": str, "content": str})
Prompt = TypedDict("Prompt", {"system": str, "query": str})


def generate_message(content: str, mode: MessageMode = "user") -> Message:
    return { "role": mode, "type": "text", "content": content }

def format_prompt(system: str, context: list[str], query: str) -> list[Message]:
    prompt = []
    prompt.append(generate_message(system, "system"))
    for chunk in context:
        prompt.append(generate_message(chunk, "user"))
    prompt.append(generate_message(query, "user"))
    return prompt


naive = Prompt(
    system=prompt_text.naive_system,
    query=prompt_text.naive_query
)

algorithmic = Prompt(
    system=prompt_text.algorithmic_system,
    query=prompt_text.algorithmic_query
)

algorithmic_ocel = Prompt(
    system=prompt_text.algorithmic_system,
    query=prompt_text.algorithmic_query_ocel
)

improved_algorithmic = Prompt(
    system=prompt_text.improved_algorithmic_system,
    query=prompt_text.improved_algorithmic_query
)

improved_algorithmic_ocel = Prompt(
    system=prompt_text.improved_algorithmic_system,
    query=prompt_text.improved_algorithmic_query_ocel
)

improved_naive = Prompt(
    system=prompt_text.improved_naive_system,
    query=prompt_text.improved_naive_query
)

improved_naive_ocel = Prompt(
    system=prompt_text.improved_naive_system,
    query=prompt_text.improved_naive_query_ocel
)

improved_naive_cascading_step_1 = Prompt(
    system=prompt_text.improved_naive_cascading_step_1_system,
    query=prompt_text.improved_naive_cascading_step_1_query
)

improved_naive_cascading_step_1_ocel = Prompt(
    system=prompt_text.improved_naive_cascading_step_1_system_ocel,
    query=prompt_text.improved_naive_cascading_step_1_query
)

improved_naive_cascading_step_2 = Prompt(
    system=prompt_text.improved_naive_cascading_step_2_system,
    query=prompt_text.improved_naive_cascading_step_2_query
)

improved_naive_cascading_step_2_ocel = Prompt(
    system=prompt_text.improved_naive_cascading_step_2_system_ocel,
    query=prompt_text.improved_naive_cascading_step_2_query
)
