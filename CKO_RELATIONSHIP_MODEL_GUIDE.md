# CKO Relationship Model Guide

## Finalidade

Use a fundação para declarar que duas entidades canônicas possuem um significado relacional explícito. Não use os modelos para representar localização física, chave estrangeira, aresta de banco, cache ou plano de travessia.

## Escolha dos endpoints

Use `RelationshipEndpoint.from_knowledge_object` quando a entidade for um Knowledge Object homologado. Use `RelationshipEndpoint.from_document` para o Document Canonical Model. Para outra entidade canônica, construa um endpoint com UUID lógico, namespace, tipo de entidade e versão semântica.

O UUID lógico identifica o objeto no domínio. `canonical_id` registra a identidade canônica correspondente quando disponível. `external_id` é informativo e não substitui o UUID lógico.

## Escolha do tipo

Escolha o tipo que expressa o significado declarado. Pares como `contains` e `contained_by`, `supports` e `supported_by`, `parent_of` e `child_of` são valores distintos. A fundação não cria automaticamente o inverso.

`related_to` deve ser reservado para declarações válidas que não possuam tipo mais específico. `equivalent_to` e `duplicates` não executam fusão de objetos. `contradicts` não executa análise semântica.

## Direção

Use `directed` quando origem e destino exercem papéis diferentes. Use `bidirectional` quando ambos os sentidos fazem parte da declaração. Use `undirected` quando a declaração não possui orientação semântica.

Para direção `bidirectional` ou `undirected`, declare `RelationshipConstraint.bidirectional=True`. Para simetria, declare também `symmetric=True`.

## Multiplicidade

A multiplicidade descreve a cardinalidade pretendida, sem enforcement externo:

- `one_to_one`: uma origem para um destino;
- `one_to_many`: uma origem para vários destinos;
- `many_to_one`: várias origens para um destino;
- `many_to_many`: várias origens para vários destinos.

A validação local confirma apenas que a declaração usa um valor oficial. Enforcement global depende de uma camada futura e não faz parte da SPR-012.

## Auto-relacionamentos

Origem e destino podem ser iguais somente quando `reflexive=True`. Essa propriedade declara compatibilidade reflexiva; ela não cria auto-relacionamentos automaticamente.

## Evidências

Adicione evidência somente quando houver origem verificável. Informe o tipo e ao menos um dos campos source, evidence, generating_algorithm, author ou pipeline. Confidence deve estar entre zero e um. Timestamp, quando presente, precisa ter timezone e será normalizado para UTC.

Evidências iguais no mesmo relacionamento são rejeitadas. Evidências diferentes podem coexistir e não são combinadas automaticamente.

## Pesos

Peso, confiança, relevância e probabilidade são independentes e opcionais. Todos usam escala normalizada de zero a um. Não presuma que um campo substitui outro e não use a fundação para calcular score.

## Estado e versão

Metadata e version precisam possuir o mesmo estado e autor. A versão segue SemVer. `parent_version` declara linhagem e não pode ser igual ao próprio `version_id`.

## Coleções e consultas

`RelationshipCollection` representa um conjunto imutável e rejeita identidade canônica duplicada. `RelationshipQuery` declara filtros e paginação. `RelationshipResult` associa uma query à página retornada e ao total conhecido.

Esses modelos não armazenam dados e não executam consultas.

## Serialização

Use `DeterministicRelationshipSerializer` nas fronteiras. Não monte envelopes JSON manualmente. A desserialização aceita somente JSON canônico e fechado e reconstrói agregados pela Factory.

## Compatibilidade futura

Uma futura Knowledge Graph Foundation poderá consumir `CanonicalRelationship` como entrada de domínio. Ela deverá manter persistência, indexação, inferência e travessia fora deste namespace.
