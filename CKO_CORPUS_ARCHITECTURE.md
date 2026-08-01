# CKO Knowledge Corpus Architecture

## Objetivo e responsabilidade exclusiva

`cko.core.corpus` representa, de forma canônica, imutável, determinística, versionável e serializável, a composição lógica de um corpus de conhecimento. O corpus é a autoridade explícita de pertencimento; ele não materializa, possui, carrega ou resolve os membros referenciados.

Não é banco de dados, repositório, workspace, sessão, diretório, storage, cache, serviço, runtime, unidade transacional, loader, índice universal, grafo obrigatório ou gerenciador operacional. Um corpus vazio é válido: a fronteira lógica pode ser identificada e versionada antes de receber membros.

## Estrutura

O agregado segue `KnowledgeCorpus -> CorpusManifest -> CorpusMemberReference`. `CorpusIdentity`, `CorpusVersion`, `CorpusMetadata` e o digest completam a raiz. Todos os onze modelos públicos são dataclasses `frozen=True, slots=True`; mappings são congelados recursivamente e sequências são tuplas.

`CorpusFactory` é a fronteira obrigatória da raiz. `CorpusBuilder` mantém apenas estado transitório local e sempre produz um novo corpus. As operações funcionais e `CorpusOperations` adicionam, removem, localizam, filtram, comparam e calculam estatísticas sem I/O ou mutação do corpus de origem.

## Identidade, versões e integridade

O namespace UUID exclusivo é `0d0ee5a8-e17e-5ae1-b9e4-7801131bf190`. `CorpusId.canonical(namespace, name)` usa UUIDv5; caminhos, banco, processo, sessão, localização e infraestrutura não participam da identidade.

As versões são formalmente distintas:

- esquema dos modelos: `CORPUS_SCHEMA_VERSION = "1.0"`;
- API/fundação: `CORPUS_VERSION = "1.0.0"`;
- envelope de serialização: `CORPUS_SERIALIZATION_VERSION = "1.0"`;
- composição lógica: `CorpusVersion(version, revision)`;
- membro: `CorpusMemberReference.member_version`.

O digest SHA-256 cobre esquema, versão de serialização, identidade, versão lógica, manifesto canônico e metadados estruturais. O próprio campo `digest` e timestamps de snapshot ficam fora do payload, evitando autorreferência e não determinismo.

## Integração e direção das dependências

| Fundação | Integração pública | Papel no corpus | Dependência |
|---|---|---|---|
| SPR-010 | `KnowledgeObject`/identidade/serializer | membro | corpus → knowledge |
| SPR-011 | `CanonicalDocument`/identidade/serializer | membro independente de seu objeto associado | corpus → documents |
| SPR-012 | `CanonicalRelationship`/identidade/serializer | membro | corpus → relationships |
| SPR-013 | `CanonicalGraph`/identidade/serializer | projeção relacional opcional | corpus → graph |
| SPR-014 | `CanonicalQuery` | explicitamente rejeitada | corpus → query apenas para rejeição tipada |
| SPR-015 | `CanonicalIndex`/identidade/serializer | projeção indexada opcional | corpus → index |

Nenhuma fundação anterior importa `corpus`. Graph e Index não são autoridades implícitas do acervo. Inventory e InventorySnapshot não são estendidos nem reutilizados. Documento e Knowledge Object associado podem ambos pertencer porque suas categorias e identidades tipadas são distintas.

## Limitações deliberadas

Não há resolução de referências, existência física, merge, sincronização, conflitos, histórico persistente, checkpoint, execução de query, atualização de índice, geração de grafo, persistência, rede, IA, embeddings, ontologias ou qualquer subsistema operacional. Extensão de categorias exige nova versão compatível do esquema fechado.
