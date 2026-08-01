# Decisão de arquitetura — gate do CKO CORE SDK v1.0

## Decisão

**CERTIFICADO COM RESSALVAS.**

O CKO CORE SDK constitui uma fundação suficientemente completa, robusta, desacoplada, testada e auditável para iniciar a modelagem e os contratos da camada semântica. A autorização não se estende a declarar release v1.0 publicada, operar persistência semântica em produção ou implementar governança/segurança sem o fechamento das ressalvas P1.

## Fundamentos objetivos

- 150 módulos e 29.411 linhas sob `cko.core`, AST válido e zero ciclos de import.
- Runtime não importa adapters; Checkpoint depende da porta Storage; UoW não importa Filesystem/SQLite.
- 686 testes aprovados; duas falhas legadas reproduzidas e isoladas.
- T/U/V/W aprovadas isoladamente: 29/28/31/26.
- wheel repetível em duas execuções, 184 entradas e SHA-256 idêntico.
- 334 exports raiz sem duplicatas; APIs de pacote coerentes com seus `__all__`.

## Condições da certificação

1. Atualizar ARCH-001 para refletir U/V/W e a árvore/API efetivas.
2. Decidir e sincronizar a versão de distribuição (`0.1.0` versus v1.0).
3. Aprovar uma raiz comum/taxonomia de exceções sem breaking change imediato.
4. Definir composition root e configuração de adapters/ports antes da persistência semântica produtiva.

## Ausência de bloqueador P0

Nenhum ciclo, acoplamento domínio→adapter, dependência externa não declarada em produção, falha nova de regressão, corrupção de build ou vazamento de payload foi encontrado. Esses fatos sustentam o gate emitido.

## Próxima Sprint recomendada

Executar uma Sprint específica de **consolidação normativa e release v1.0**, limitada a decisão/versionamento, atualização da ARCH-001, taxonomias e composition root. Somente após homologação iniciar a Knowledge Object Foundation. Esta decisão não inicia essa Sprint.
