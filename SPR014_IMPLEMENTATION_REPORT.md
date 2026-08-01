# SPR-014 — Knowledge Query Foundation — Relatório de Implementação

## Identificação

- Sprint: SPR-014
- Componente: Knowledge Query Foundation
- Namespace: `cko.core.query`
- Schema: `1.0`
- Versão: `1.0.0`
- Plataforma: Windows 10, Windows 11, PowerShell 5.1, Python 3.13 e UTF-8
- Data de validação: 2026-07-26

## Resultado

Foi implementado o modelo canônico, imutável, versionado e determinístico de intenção de consulta. A entrega não contém execução, persistência, indexação, busca textual, busca semântica, inferência, embeddings, IA, LLM, cache, otimização ou ranqueamento.

## Arquivos de código

- `src/cko/core/query/__init__.py`
- `src/cko/core/query/contracts.py`
- `src/cko/core/query/errors.py`
- `src/cko/core/query/enums.py`
- `src/cko/core/query/factory.py`
- `src/cko/core/query/identity.py`
- `src/cko/core/query/metadata.py`
- `src/cko/core/query/models.py`
- `src/cko/core/query/serializer.py`
- `src/cko/core/query/validator.py`
- `src/cko/core/__init__.py`

## Modelos entregues

Foram entregues `QueryId`, `QueryIdentity`, `QueryMetadata`, `QueryExpression`, `QueryFilter`, `QueryConstraint`, `QueryOrdering`, `QueryProjection`, `QueryPagination`, `QueryDescriptor`, `CanonicalQuery`, `QueryResult`, `QueryCollection` e `QueryStatistics`.

## Contratos e validações

Todos os modelos são frozen e slotted, possuem versão de schema e discriminador, normalizam instantes para UTC, aplicam deep freeze e participam de serialização determinística com round-trip. A validação cobre operadores, dimensões de filtro, expressões, paginação, ordenação, alvos, estados, duplicidades, totais, estatísticas e composição estrutural.

## API pública

A API completa está publicada em `cko.core.query`. A raiz `cko.core` preserva os símbolos anteriores da Discovery Foundation e acrescenta aliases canônicos para os cinco nomes conflitantes. Nenhum contrato público homologado foi substituído.

## Integração

`QueryResult` integra exclusivamente os modelos públicos de Knowledge Objects, Document Canonical Model, Knowledge Relationship Foundation e Knowledge Graph Foundation. A serialização delega a restauração aos serializadores públicos dessas quatro fundações.

## Testes dedicados e cobertura

- Arquivo: `tests/test_knowledge_query_foundation_spr014.py`
- Resultado: 19 testes aprovados
- Cobertura do namespace `cko.core.query`: 99%
- Linhas mensuradas: 937
- Linhas não cobertas: 10
- Requisito mínimo: 95%

## Regressão completa

- Testes coletados: 827
- Aprovados: 825
- Falhas legadas: 2
- Regressões atribuíveis à SPR-014: 0

As duas falhas legadas são independentes do namespace implementado. Uma decorre de duas suítes antigas exigirem assinaturas incompatíveis para `cko.metadata.file_metadata.collect_metadata`. A outra decorre de uma conexão SQLite aberta pelo teste legado `test_existing_table_is_preserved`, impedindo a remoção do banco temporário no Windows. Esses contratos não foram alterados porque estão fora do escopo exclusivo autorizado e a Sprint proíbe mudanças em APIs públicas homologadas.

## Serialização

Foram validados UTF-8, ordenação de chaves, schema fechado, ausência de NaN e infinitos, rejeição de JSON não canônico, round-trip de todos os modelos, preservação de datetime em valores abertos e digest SHA-256.

## Validação integrada

- Suítes SPR-010 a SPR-014 executadas em conjunto: 122 testes aprovados
- Símbolos obrigatórios da API da SPR-014: 17 validados
- Símbolos públicos do namespace: 34 validados
- Contratos anteriores da Discovery Foundation: preservados

## Build oficial

- Comando: `CKO_BUILD.cmd`
- Resultado: aprovado
- Artefato: `runtime/reports/build/cko-1.0.0-py3-none-any.whl`
- Arquivos no wheel: 241
- Arquivos do namespace `cko.core.query` no wheel: 10
- Tamanho validado do artefato: 377862 bytes
- SHA-256 do wheel: `8c57cdc5ce5978e3869a5dbada113201a664f69c4d72bbff679df7b8347ac36f`
- Importação isolada diretamente do wheel: aprovada
- Round-trip canônico diretamente do wheel: aprovado
- Compatibilidade dos aliases públicos diretamente do wheel: aprovada

## Restrições arquiteturais

O namespace não importa nem integra Storage, Runtime, SQLite, Filesystem, Search Engine, SQL, Neo4j, Elasticsearch, Vector Database, IA, embeddings ou LLM.

## Encerramento

A SPR-014 foi implementada sem iniciar Sprint posterior. A entrega permanece aguardando homologação formal da Knowledge Query Foundation.
