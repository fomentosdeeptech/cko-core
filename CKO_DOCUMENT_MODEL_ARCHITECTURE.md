# CKO Document Canonical Model — Arquitetura

## Finalidade

O namespace `cko.core.documents` estabelece a representação canônica de uma unidade documental lógica. O documento não é confundido com arquivo, formato, localização, conteúdo extraído ou mecanismo de persistência. PDF, DOCX, HTML, imagem e demais formatos são descritos exclusivamente como representações físicas.

## Limites arquiteturais

O módulo depende somente da fundação pública de Knowledge Objects e da hierarquia consolidada de exceções do CORE. Não possui dependências de Storage, Runtime, Discovery, Checkpoint, Unit of Work, Filesystem ou SQLite.

Não fazem parte desta arquitetura: parser, OCR, extração de conteúdo, indexação, cache, embeddings, inferência, LLM, busca semântica, grafo, ontologia, taxonomia e repositórios.

## Camadas internas

| Camada | Responsabilidade |
|---|---|
| `contracts.py` | Versão de schema, protocolos, normalização, deep freeze e envelopes fechados |
| `enums.py` | Vocabulários oficiais de tipo, formato, estado, idioma, origem e integridade |
| `identity.py` | Identidade lógica, documental, física, externa e vínculo com Knowledge Object |
| `metadata.py` | Autoria, idioma, fontes e metadados descritivos |
| `models.py` | Descritores, representações, versões, estatísticas, integridade, direitos e agregados |
| `validator.py` | Invariantes estruturais e cruzadas |
| `factory.py` | Fronteira obrigatória de construção de agregados |
| `serializer.py` | JSON canônico determinístico e round-trip estrito |
| `errors.py` | Falhas documentais derivadas de `CKOError` |

## Agregado canônico

`CanonicalDocument` contém `DocumentIdentity`, `DocumentMetadata`, `DocumentDescriptor`, `DocumentContentDescriptor`, um `KnowledgeObject` homologado, zero ou mais representações, uma linhagem de versões, estatísticas opcionais, integridade opcional e direitos opcionais.

O agregado só pode ser instanciado por `DocumentFactory`. A Factory constrói o `KnowledgeObject` associado por `KnowledgeObjectFactory`, usando `KnowledgeType.COMPOSITE`, o mesmo identificador lógico e o mesmo namespace. O contrato de Knowledge Objects não foi alterado.

`DocumentCollection` também possui criação exclusiva pela Factory e impede duplicidade de identidade documental canônica.

## Identidades

`DocumentIdentity` separa quatro dimensões:

- `logical_id`: continuidade lógica do documento;
- `document_id`: identidade documental canônica derivada de namespace e identidade lógica;
- `physical_ids`: identificadores de manifestações físicas, sem armazenar arquivos;
- `external_ids`: pares nomeados de identidades externas.

`knowledge_object_id` vincula a especialização documental à Knowledge Object Foundation. Seu UUID deve coincidir com `logical_id`.

## Representações físicas

`DocumentRepresentation` armazena somente formato, MIME type, encoding, extensão, compressão e hash SHA-256. O modelo não possui payload, caminho, stream, bytes ou comportamento de formato.

São reconhecidos PDF, DOCX, TXT, RTF, ODT, XLSX, ODS, CSV, PPTX, ODP, HTML, XML, JSON, Markdown, e-mail, imagem, OCR, áudio transcrito, vídeo transcrito e formato não classificado.

## Imutabilidade e tempo

Todos os modelos públicos são `dataclass(frozen=True, slots=True)`. Coleções são convertidas para tuplas. Mapeamentos são ordenados e protegidos por `MappingProxyType`. Números não finitos são recusados. Instantes precisam ser timezone-aware e são normalizados para UTC.

## Invariantes do agregado

- identidade lógica documental e identidade lógica do Knowledge Object coincidem;
- namespaces documental e do Knowledge Object coincidem;
- versão corrente documental e versão do Knowledge Object coincidem;
- todo documento possui ao menos uma fonte;
- versões, representações, fontes, autores, hashes e identificadores não admitem duplicidades;
- a última versão declarada coincide com a versão dos metadados;
- checksum dos metadados e SHA-256 de integridade coincidem quando ambos existem;
- tamanho lógico do conteúdo e tamanho lógico de integridade coincidem quando ambos existem;
- identidade física exige ao menos uma representação;
- integridade verificada exige `is_intact=True`; divergência exige `is_intact=False`.

## API no composition boundary

O namespace é exportado pelo pacote CORE. Como `cko.core` já possuía um `CanonicalDocument` legado homologado, o novo agregado é publicado no topo como `DocumentCanonicalModel`, preservando o contrato anterior. O nome `CanonicalDocument` permanece oficial dentro de `cko.core.documents`.

Factory, Validator e Serializer são componentes independentes e injetáveis, aptos a serem fornecidos pelo Composition Root sem acoplamento a infraestrutura. Nenhum componente de infraestrutura foi incorporado nesta Sprint.
