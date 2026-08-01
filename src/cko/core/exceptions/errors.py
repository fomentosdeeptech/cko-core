"""Exceções estáveis para falhas nas fronteiras do núcleo canônico."""


class CKOError(Exception):
    """Base de todas as exceções explicitamente emitidas pelo SDK."""


class ContractError(CKOError):
    """Indica violação de um contrato público do SDK."""


class ModelValidationError(ContractError, ValueError):
    """Indica estado inválido ao construir um modelo canônico."""


class IdentityError(ModelValidationError):
    """Indica identidade ou versão canônica inválida."""


class MetadataError(ModelValidationError):
    """Indica metadados universais inconsistentes."""


class ConfigurationError(CKOError):
    """Indica configuração ausente, inválida ou não suportada."""


class CompositionError(CKOError):
    """Indica falha na composição canônica dos componentes do SDK."""
