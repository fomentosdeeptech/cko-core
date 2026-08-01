"""Fronteira futura de inventário incremental.

A implementação operacional permanece nos módulos atuais até migração formal.
"""


class InventoryService:
    @property
    def enabled(self) -> bool:
        return False
