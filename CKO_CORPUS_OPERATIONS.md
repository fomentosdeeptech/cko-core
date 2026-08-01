# CKO Corpus Operations

Todas as operações são puras, determinísticas, in-memory e livres de I/O.

| Operação | Resultado | Invariante |
|---|---|---|
| `contains_member` | booleano | compara identidade tipada |
| `find_member` | referência ou `None` | não resolve o membro |
| `filter_members` | tupla ordenada | categoria fechada |
| `add_member` | novo `KnowledgeCorpus` | rejeita duplicidade e incrementa revisão |
| `remove_member` | novo `KnowledgeCorpus` | rejeita ausência e incrementa revisão |
| `compare_corpora` | `CorpusComparisonResult` | resultados canonicamente ordenados |
| `corpus_statistics` | `CorpusStatistics` | deriva somente do manifesto |

`CorpusOperations` expõe aliases estáticos dessas funções. A unidade de pertencimento é `(category, namespace, member_id)`. Alterações de versão, digest, discriminador ou atributos são detectadas em comparações de referências com a mesma identidade.

`CorpusBuilder` é apropriado para composições incrementais. Ele aceita referências ou agregados públicos homologados, mantém um mapa local para detectar duplicidade e só produz estado canônico em `build()`. Não modifica corpora existentes, acessa recursos, executa queries, atualiza grafos/índices ou mantém estado externo.

Não existem operações de merge, sincronização, conflito, transação, persistência, carregamento, discovery, checkpoint ou gerenciamento de ciclo de vida.
