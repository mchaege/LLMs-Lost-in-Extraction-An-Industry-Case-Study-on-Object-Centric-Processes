from src import prompt
from pathlib import Path
from src import data_import
from collections import namedtuple
from .ai import OcelEntity, AiWorker


def run_experiment(
    model_name: str, 
    prompt_variant_names: list[str],
    context_file_path: str, 
    chunking_func: data_import.chunk_generator = data_import.non_chunker, 
    runs: int = 5, 
    show_token_usage: bool = False
) -> list[OcelEntity]:
    
    client = AiWorker(model_name, OcelEntity)
    context = chunking_func(data_import.load_context_from_file(context_file_path))

    responses = []
    for i in range(1, runs + 1):
        previous_results = ""

        for prompt_variant_name in prompt_variant_names:

            prompt_variant = getattr(prompt, prompt_variant_name, None)
            messages = prompt.format_prompt(prompt_variant["system"], context, prompt_variant["query"])
            if previous_results != "":
                messages.insert(1, prompt.generate_message(previous_results))

            response: OcelEntity = client.invoke(messages, show_token_usage)

            previous_results = response.model_dump_json()
            
            responses.append(response)
            p = Path(fr"response_data\{model_name}\{chunking_func.__name__}\{prompt_variant_name}\response_{i}.json")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(response.model_dump_json(indent=4), encoding="utf-8")
    return responses


def load_experiment(*file_paths: str) -> list[OcelEntity]:
    entities = []
    for file_path in file_paths:
        p = Path(file_path)
        if p.exists():
            entities.append(
                OcelEntity.model_validate_json(
                    p.read_text(encoding="utf-8")
                )
            )
    return entities

ExperimentSetting = namedtuple("ExperimentSetting", [
    "model", "prompt_variants", "chunker"
])

def print_experiment_settings(self: ExperimentSetting) -> str:
    return f"ExperimentSettings(model: {self.model}, prompt_variants: {", ".join(self.prompt_variants)}, chunker: {self.chunker.__name__})"

ExperimentSetting.__str__ = print_experiment_settings