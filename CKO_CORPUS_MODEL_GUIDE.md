# CKO Knowledge Corpus Model Guide

## Criar um corpus

Use `CorpusFactory`. Uma referência mínima contém `member_id`, categoria fechada, versão individual, discriminador público, namespace, digest SHA-256 opcional e atributos estruturais opcionais. Ela nunca contém o objeto, loader, caminho ou handle externo.

`CorpusFactory.create_corpus(name=..., namespace=..., members=...)` normaliza o manifesto, deriva a identidade UUIDv5, cria `CorpusVersion`, congela metadados e calcula o digest. A construção direta de `KnowledgeCorpus` é rejeitada.

## Invariantes

- identidade do membro é `(categoria, namespace, member_id)`;
- uma identidade aparece no máximo uma vez no manifesto;
- versão ou digest diferentes da mesma identidade representam alteração entre corpora, não dois membros simultâneos;
- a ordem é canônica por categoria, namespace, ID, versão, digest e discriminador;
- categorias admitidas: Knowledge Object, Document, Relationship, Graph e Index;
- Query nunca é membro;
- Graph e Index são projeções opcionais, não autoridade da totalidade;
- nenhum membro ou categoria é obrigatório; corpus vazio é válido;
- versão do corpus e versões dos membros são independentes;
- metadados participam do digest e, portanto, são estruturais.

## Evolução imutável

`add_member` e `remove_member` retornam um novo corpus com revisão incrementada. `CorpusBuilder.from_corpus` prepara uma nova revisão sem modificar a anterior. Mudança deliberada do SemVer lógico é feita na criação de uma nova representação; não existem migrações automáticas.

## Snapshot e estatísticas

`CorpusSnapshot` copia identidade de origem, versão, manifesto, digest e estatísticas. Seu ID deriva deterministicamente do corpus; `captured_at` é informativo e não participa do digest nem do ID. O snapshot não é backup, checkpoint, arquivo ou histórico persistente.

`CorpusStatistics` usa apenas as referências declaradas: total, quantidade com digest, categorias presentes, contagem por categoria e por versão. Nenhum membro é acessado.

## Comparação

`compare_corpora` devolve `CorpusComparisonResult` com `added`, `removed`, `preserved` e `changed`. Cada `CorpusReferenceChange` distingue `version_changed` e `digest_changed`; alterações em discriminador/atributos também permanecem estruturadas. Não há merge ou resolução de conflito.
