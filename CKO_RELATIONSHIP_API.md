# CKO Relationship API

## Importação

A API principal está em `cko.core.relationships`. Os modelos e serviços também são reexportados por `cko.core`. Como `cko.core` já possuía o enum legado de relacionamentos internos de Knowledge Objects, o enum completo da SPR-012 é reexportado na raiz como `CanonicalRelationshipType`. Dentro do novo namespace, seu nome oficial permanece `RelationshipType`.

## Constantes

- `RELATIONSHIP_SCHEMA_VERSION`: versão do schema fechado.
- `RELATIONSHIP_VERSION`: versão da fundação.

## Construção

`RelationshipFactory.create` recebe namespace, endpoints, tipo e autor. Aceita direção, restrição, evidências, pesos, estado, força, versão, identidade lógica, versão pai, origem, atributos, label e descrição.

`RelationshipFactory.from_parts` é a fronteira validada para reconstrução de um agregado completo. `RelationshipFactory.create_collection` cria coleções com validação de duplicidade.

`CanonicalRelationship` e `RelationshipCollection` recusam construção direta.

## Identidade e integração

- `RelationshipId.new`: cria identidade lógica UUID v4.
- `RelationshipId.canonical`: cria identidade canônica UUID v5.
- `RelationshipId.parse`: converte UUID textual.
- `RelationshipEndpoint.from_knowledge_object`: adapta `KnowledgeObject` homologado.
- `RelationshipEndpoint.from_document`: adapta `CanonicalDocument` homologado.

## Modelos

- `RelationshipId`
- `RelationshipIdentity`
- `RelationshipMetadata`
- `RelationshipEndpoint`
- `RelationshipDirection`
- `RelationshipConstraint`
- `RelationshipEvidence`
- `RelationshipWeight`
- `RelationshipVersion`
- `RelationshipDescriptor`
- `CanonicalRelationship`
- `RelationshipCollection`
- `RelationshipQuery`
- `RelationshipResult`

Todos são dataclasses frozen, slotted, versionados e discriminados.

## Enums

- `RelationshipType`
- `RelationshipStatus`
- `RelationshipDirectionType`
- `RelationshipEvidenceType`
- `RelationshipConstraintType`
- `RelationshipStrength`

## Serviços

- `RelationshipFactory`: construção obrigatória dos agregados.
- `RelationshipValidator`: validação estrutural e cruzada.
- `DeterministicRelationshipSerializer`: JSON canônico, round-trip e digest SHA-256.

## Protocolos

- `RelationshipSerializer`
- `RelationshipValidatorContract`

Os protocolos permitem injeção pelo Composition Root sem vincular a fundação a infraestrutura.

## Exceções

- `RelationshipError`
- `RelationshipValidationError`
- `RelationshipSerializationError`
- `RelationshipFactoryError`
- `RelationshipIdentityError`
- `RelationshipConstraintError`
- `RelationshipEvidenceError`

Todas derivam de `CKOError`. `RelationshipError.to_dict` fornece código, detalhes, mensagem e modelo em formato seguro.

## Garantias

A API não persiste, não consulta, não infere, não percorre e não indexa relacionamentos. `RelationshipQuery` e `RelationshipResult` são contratos de dados neutros para fronteiras futuras; eles não implementam mecanismo de consulta.
