"""Carregamento determinístico de configuração JSON, TOML e ambiente."""

from __future__ import annotations

import json
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from cko.core.exceptions import ConfigurationError
from cko.core.utils import require_non_empty


ConfigScalar = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class SDKConfig:
    """Configuração mínima do SDK, extensível por valores escalares."""

    environment: str = "development"
    log_level: str = "INFO"
    service_name: str = "cko-core"
    values: Mapping[str, ConfigScalar] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("environment", "log_level", "service_name"):
            if not isinstance(getattr(self, field_name), str):
                raise ConfigurationError(f"{field_name} deve ser texto")
        object.__setattr__(
            self,
            "environment",
            require_non_empty(self.environment, "environment"),
        )
        log_level = require_non_empty(self.log_level, "log_level").upper()
        if log_level not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
            raise ConfigurationError(f"log_level inválido: {log_level}")
        object.__setattr__(self, "log_level", log_level)
        object.__setattr__(
            self,
            "service_name",
            require_non_empty(self.service_name, "service_name"),
        )
        copied_values = dict(self.values)
        if any(not isinstance(key, str) or not key for key in copied_values):
            raise ConfigurationError("chaves de values devem ser textos não vazios")
        scalar_types = (str, int, float, bool, type(None))
        if any(not isinstance(value, scalar_types) for value in copied_values.values()):
            raise ConfigurationError("values aceita apenas valores escalares")
        object.__setattr__(self, "values", MappingProxyType(copied_values))


def _read_file(path: Path) -> dict[str, object]:
    try:
        if path.suffix.lower() == ".toml":
            with path.open("rb") as stream:
                loaded = tomllib.load(stream)
        elif path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8") as stream:
                loaded = json.load(stream)
        else:
            raise ConfigurationError("formato suportado: .toml ou .json")
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"falha ao carregar configuração: {path}") from exc
    if not isinstance(loaded, dict):
        raise ConfigurationError("a raiz da configuração deve ser um objeto")
    section = loaded.get("cko", loaded)
    if not isinstance(section, dict):
        raise ConfigurationError("a seção 'cko' deve ser um objeto")
    return section


def load_config(
    path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> SDKConfig:
    """Combina arquivo opcional e variáveis ``CKO_*`` com precedência do ambiente."""
    data = _read_file(Path(path)) if path is not None else {}
    env = os.environ if environ is None else environ
    known = {
        "environment": data.pop("environment", "development"),
        "log_level": data.pop("log_level", "INFO"),
        "service_name": data.pop("service_name", "cko-core"),
    }
    env_keys = {
        "environment": "CKO_ENVIRONMENT",
        "log_level": "CKO_LOG_LEVEL",
        "service_name": "CKO_SERVICE_NAME",
    }
    for field_name, env_name in env_keys.items():
        if env_name in env:
            known[field_name] = env[env_name]
    values: dict[str, ConfigScalar] = {}
    for key, value in data.items():
        if not isinstance(value, (str, int, float, bool, type(None))):
            raise ConfigurationError(f"valor não escalar em 'cko.{key}'")
        values[key] = value
    prefix = "CKO_VALUE_"
    for key, value in env.items():
        if key.startswith(prefix):
            values[key.removeprefix(prefix).lower()] = value
    return SDKConfig(values=values, **known)
