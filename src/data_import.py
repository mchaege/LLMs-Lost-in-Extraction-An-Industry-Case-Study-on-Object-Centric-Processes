from pathlib import Path
from typing import Callable



chunk_generator = Callable[[str], list[str]]

def non_chunker(text: str) -> list[str]:
    return [text]

def sentence_chunker(text: str) -> list[str]:
    return text.replace(". ", "\n").splitlines()

def section_chunker(text: str) -> list[str]:
    sections = []
    section = {
        "heading": "",
        "text": []
    }
    for line in text.splitlines():
        if line.endswith(".") or line.startswith("Fig. "):
            section["text"].append(line)
        else:
            if section["heading"] == "":
                section["heading"] = line
            else:
                sections.append("\n".join([section["heading"], *section["text"]]))
                section = {"heading": "", "text": []}        
    
    sections.append("\n".join((section["heading"], *section["text"])))
    return sections


def load_context_from_file(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise Exception(f"file: '{file_path}' not found")
    
    file_content = p.read_text(encoding="utf-8")
    return file_content