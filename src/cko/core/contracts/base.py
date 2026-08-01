"""Ports fundamentais compartilhados pelos consumidores do CKO CORE SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable

from cko.core.identity import CanonicalId, SemanticVersion
from cko.core.models import CanonicalEvent


class Identifiable(Protocol):
    """Objeto que expõe uma identidade canônica imutável."""

    @property
    def id(self) -> CanonicalId:
        """Retorna a identidade canônica do objeto."""
        raise NotImplementedError


T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class Repository(Protocol[T_co]):
    """Porta mínima de leitura para repositórios substituíveis."""

    def get(self, entity_id: CanonicalId) -> T_co | None:
        """Obtém uma entidade pela identidade ou retorna ``None``."""
        raise NotImplementedError

    def contains(self, entity_id: CanonicalId) -> bool:
        """Informa se a identidade está disponível no repositório."""
        raise NotImplementedError


@runtime_checkable
class Clock(Protocol):
    """Fonte substituível de tempo para código determinístico."""

    def now(self) -> datetime:
        """Retorna o instante atual com fuso horário."""
        raise NotImplementedError


@runtime_checkable
class EventPublisher(Protocol):
    """Porta de publicação de eventos canônicos."""

    def publish(self, event: CanonicalEvent) -> None:
        """Publica um evento sem determinar o mecanismo de transporte."""
        raise NotImplementedError


@runtime_checkable
class Plugin(Protocol):
    """Contrato de extensão versionada do SDK."""

    @property
    def name(self) -> str:
        """Retorna o nome estável do plugin."""
        raise NotImplementedError

    @property
    def version(self) -> SemanticVersion:
        """Retorna a versão semântica implementada pelo plugin."""
        raise NotImplementedError

    def start(self) -> None:
        """Inicializa recursos controlados pelo plugin."""
        raise NotImplementedError

    def stop(self) -> None:
        """Libera recursos controlados pelo plugin."""
        raise NotImplementedError

