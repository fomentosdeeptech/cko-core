# CKO Document Canonical Model — API Pública

## Namespace

A API oficial reside em `cko.core.documents`. No topo de `cko.core`, o novo agregado é exposto como `DocumentCanonicalModel` para preservar o `CanonicalDocument` legado.

## Constantes e contratos

| Símbolo | Contrato |
|---|---|
| `DOCUMENT_SCHEMA_VERSION` | Versão `1.0` do schema documental |
| `DOCUMENT_VERSION` | Versão `1.0.0` da implementação |
| `DocumentSerializer` | Protocolo de serialize, deserialize e digest |
| `DocumentValidatorContract` | Protocolo de validação documental |

## Enums

| Enum | Finalidade |
|---|---|
| `DocumentType` | Natureza lógica do documento |
| `DocumentFormat` | Formato de uma representação física |
| `DocumentStatus` | Estado de ciclo de vida |
| `DocumentLanguageCode` | Código oficial de idioma |
| `DocumentSourceType` | Natureza de uma origem |
| `IntegrityStatus` | Estado da verificação de integridade |

## Identidade

| Modelo | Campos sem controle de schema |
|---|---|
| `DocumentId` | `value` |
| `DocumentIdentity` | `logical_id`, `document_id`, `knowledge_object_id`, `namespace`, `physical_ids`, `external_ids` |

`DocumentId.new` cria identidade lógica aleatória. `DocumentId.canonical` deriva a identidade documental por UUID v5. `DocumentId.parse` normaliza UUID textual ou nativo.

## Metadados

| Modelo | Responsabilidade |
|---|---|
| `DocumentLanguage` | Código, locale e nome de idioma |
| `DocumentAuthor` | Nome, identificador, organização e papel |
| `DocumentSource` | Tipo, identificador, origem, identidade externa e data de recuperação |
| `DocumentMetadata` | Título, autoria, idioma, classificação, licenciamento, fontes, datas, versão e confiança |

`DocumentMetadata` inclui título, subtítulo, autor, coautores, criador, editor, idioma, palavras-chave, tags, domínio, categoria, licença, origens, checksum, criação, modificação, publicação, organização, versão e confiança.

## Modelos documentais

| Modelo | Responsabilidade |
|---|---|
| `DocumentDescriptor` | Tipo lógico, status e resumo |
| `DocumentContentDescriptor` | Tipo lógico de conteúdo, referências a fragmentos e extrações futuras, tamanho lógico |
| `DocumentRepresentation` | Metadados de uma manifestação física |
| `DocumentVersion` | Identidade, autoria, instante, estado, ancestral e checksum de versão |
| `DocumentStatistics` | Contadores opcionais de páginas, caracteres, palavras, linhas, tabelas, imagens, anexos e links |
| `DocumentIntegrity` | SHA-256, tamanhos, assinatura, indicador e status de integridade |
| `DocumentRights` | Licença, titular, acesso e expiração |
| `CanonicalDocument` | Raiz do agregado documental |
| `DocumentCollection` | Coleção imutável e sem duplicidades |

## Serviços

### `DocumentFactory`

`create` é a fronteira oficial para criação de `CanonicalDocument`. Recebe namespace, metadados, descritor, criador e componentes opcionais. A operação cria as identidades, cria o `KnowledgeObject`, cria a versão inicial e executa validação completa.

`from_parts` reconstrói um agregado a partir de modelos existentes e executa validação completa. É usada pelo serializer.

`create_collection` é a fronteira oficial para criação de `DocumentCollection`.

### `DocumentValidator`

`validate` aceita qualquer modelo documental público. Além de schema, imutabilidade e discriminador, valida invariantes cruzadas de `CanonicalDocument` e `DocumentCollection`.

### `DeterministicDocumentSerializer`

`serialize` retorna bytes JSON UTF-8 canônicos. `deserialize` reconstrói e valida o modelo. `from_dict` reconstrói um envelope já decodificado. `digest` retorna SHA-256 da serialização canônica.

## Exceções

| Exceção | Condição |
|---|---|
| `DocumentError` | Raiz documental, derivada de `CKOError` |
| `DocumentValidationError` | Campo ou invariante inválida |
| `DocumentSerializationError` | Payload inválido ou não canônico |
| `DocumentFactoryError` | Violação da fronteira de criação ou falha de construção |

Não existe raiz de exceções paralela ao CORE.
