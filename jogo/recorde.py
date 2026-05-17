"""Guarda a maior pontuação em um arquivo na pasta do usuário."""

import json
from pathlib import Path

ARQUIVO = Path.home() / ".pug_lua_vermelha.json"


def carregar() -> int:
    try:
        return int(json.loads(ARQUIVO.read_text(encoding="utf-8")).get("recorde", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def salvar(pontos: int) -> bool:
    """Salva se for um novo recorde. Devolve True quando bateu o recorde."""
    if pontos <= carregar():
        return False
    try:
        ARQUIVO.write_text(json.dumps({"recorde": pontos}), encoding="utf-8")
    except OSError:
        pass
    return True
