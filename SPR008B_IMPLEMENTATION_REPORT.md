# SPR-008B — CKO CORE SDK — Relatório de Implementação

## Identificação

- Sprint: SPR-008B
- Objeto: Modelo Canônico de Ativos do CKO
- Workspace: `G:\Meu Drive\01 - CKO Platform\01_Projects\CKO\CORE`
- Baseline aplicada: Baseline Arquitetural 1.0
- Fundação homologada: SPR-008A — namespace `cko.core`
- Data da validação: 14/07/2026

## Resultado

O Modelo Canônico de Ativos foi implementado como extensão aditiva do namespace
`cko.core`. O modelo é imutável, completamente tipado, validado na construção,
identificado por `CanonicalId` e independente de infraestrutura. A API pública é
exportada por `cko.core.models` e por `cko.core`.

Nenhum módulo legado foi movido ou removido. Baseline, Governança, Discoveries,
banco canônico, Persistence e motores operacionais não foram alterados.

## Entidades criadas

### Raiz e especializações

- `Asset`: entidade raiz para qualquer ativo do ecossistema;
- `DocumentAsset`: documento textual ou paginado, sem parser ou OCR;
- `ImageAsset`: imagem com dimensões canônicas opcionais;
- `AudioAsset`: áudio com duração canônica opcional;
- `VideoAsset`: vídeo com duração e dimensões canônicas opcionais;
- `ProjectAsset`: projeto lógico independente de ferramenta ou repositório;
- `DatabaseAsset`: base de dados como ativo lógico, sem conexão;
- `KnowledgeAsset`: unidade de conhecimento sem RAG, embeddings ou Graph;
- `FolderAsset`: contêiner lógico, sem caminho de filesystem;
- `ReferenceAsset`: referência a outro `CanonicalId` ou a uma URI explícita.

### Tipos associados

- `AssetRelation`: relação identificada entre dois ativos distintos;
- `AssetFingerprint`: assinatura de identificação não criptográfica;
- `AssetHash`: digest ou checksum, com validação de algoritmos conhecidos;
- `AssetClassification`: atribuição de taxonomia com confiança opcional;
- `AssetStatus`: disponibilidade operacional do ativo;
- `AssetLifecycle`: estágio universal do ciclo de vida.

## Relacionamentos

`Asset` agrega classificações, fingerprints e hashes somente quando todos
referenciam o mesmo `CanonicalId` do ativo. `AssetRelation` usa exclusivamente
`source_asset_id` e `target_asset_id`; não incorpora mecanismo de Graph nem
mantém objetos ou adaptadores externos. Autorrelacionamentos são rejeitados.

`ReferenceAsset` representa uma referência como dado canônico. Ele não acessa a
URI e não resolve o ativo de destino. `FolderAsset` representa agrupamento
lógico e não contém caminho, handle ou operação de filesystem.

## Decisões arquiteturais

1. Todas as entidades são `dataclass` congeladas com `slots` quando apropriado.
2. Igualdade e hash de entidades usam `CanonicalId`, preservando identidade
   mesmo quando atributos descritivos evoluem.
3. Extensões de metadados são copiadas e congeladas recursivamente.
4. Datas exigem fuso horário e são normalizadas para UTC.
5. A serialização usa envelope versionado `schema_version = "1.0"`, discriminador
   `kind`, datas ISO 8601 e JSON determinístico.
6. A desserialização seleciona somente tipos registrados no SDK e rejeita versão,
   tipo ou campo desconhecido, impedindo entidades paralelas silenciosas.
7. `AssetStatus` e `AssetLifecycle` são enums fechados porque representam
   vocabulários universais, não entidades com ciclo de identidade próprio.
8. Campos especializados descrevem propriedades do ativo; não executam leitura,
   descoberta, classificação, persistência ou integração.

## Compatibilidade com a SPR-008A

A implementação reutiliza diretamente `CanonicalId`, `UniversalMetadata` e os
utilitários de data/texto homologados na SPR-008A. Os modelos anteriores
(`CanonicalDocument`, `DocumentLocation`, `InventoryItem` e `CanonicalEvent`)
continuam exportados sem alteração de assinatura. A suíte da SPR-008A passou
junto com a nova suíte.

O desenho segue a evolução incremental da Baseline 1.0: um novo módulo foi
adicionado em `src/cko/core/models`, e apenas os arquivos públicos de exportação
do namespace foram atualizados.

## Dependências e acoplamento

O runtime utiliza somente a biblioteca padrão do Python e componentes já
homologados de `cko.core`. Não existem imports ou operações de:

- SQLite ou qualquer banco;
- Discovery ou filesystem;
- OCR, IA ou APIs;
- embeddings ou RAG;
- Graph;
- Persistence.

`DatabaseAsset`, `FolderAsset` e `ReferenceAsset` são representações de domínio;
seus nomes não implicam conexão, acesso a disco ou chamada externa.

## Arquivos

### Criado no SDK

- `src/cko/core/models/asset.py`

### API pública atualizada

- `src/cko/core/models/__init__.py`
- `src/cko/core/__init__.py`

### Testes criados

- `tests/test_canonical_asset_model_spr008b.py`

### Documentação criada

- `SPR008B_IMPLEMENTATION_REPORT.md`

## Validação técnica

Comando da suíte da Sprint e regressão da fundação:

```powershell
$env:PYTHONPATH = "src"
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest `
  tests\test_canonical_asset_model_spr008b.py `
  tests\test_core_sdk_spr008a.py `
  -q -p no:cacheprovider
```

Resultado:

```text
26 passed in 0.97s
```

Os 17 testes da SPR-008B cobrem:

- construção dos dez tipos de ativo;
- serialização e desserialização de todos os subtipos;
- igualdade e hash orientados por `CanonicalId`;
- relações e rejeição de autorrelacionamento;
- hashes e validação de digest;
- fingerprints e classificações;
- metadados recursivamente imutáveis;
- estados, lifecycle, dimensões e datas;
- rejeição de versões, tipos e campos desconhecidos.

A tentativa da suíte legada completa avançou por 29 testes, mas não pôde ser
concluída porque o sandbox negou ao `pytest` a enumeração e limpeza de seu
diretório temporário (`PermissionError: [WinError 5]`). Essa limitação ambiental
é compatível com a já registrada na SPR-008A e não indica falha do novo modelo.
Nenhum banco canônico foi aberto ou alterado.

Validações adicionais:

- análise AST dos quatro arquivos da Sprint: aprovada;
- imports proibidos no novo módulo: nenhum;
- dependência externa no novo módulo: nenhuma;
- arquivos Python em UTF-8;
- nenhuma linha acima de 88 caracteres após revisão final.

## Próximos passos

1. Homologar formalmente a API pública da SPR-008B.
2. Exigir que motores futuros recebam e produzam `Asset` e seus tipos associados,
   sem definir entidades concorrentes.
3. Criar testes contratuais para cada motor quando seu escopo for aprovado.
4. Definir políticas de transição de status/lifecycle em Sprint própria; o modelo
   atual valida estados, mas deliberadamente não implementa workflow.
5. Reexecutar a suíte legada completa em ambiente com temporário gravável.

## Respostas de validação

1. **O Modelo Canônico de Ativos foi implementado?** Sim. A raiz, as nove
   especializações e os tipos associados solicitados estão públicos e testados.
2. **Todos os motores futuros poderão reutilizá-lo?** Sim. O modelo é neutro de
   motor e infraestrutura, e está disponível na API pública de `cko.core`.
3. **Existe dependência externa?** Não no runtime do modelo. `pytest` é utilizado
   somente na validação.
4. **Existe acoplamento com infraestrutura?** Não. Não há conexão, I/O, caminho,
   adaptador, API ou mecanismo de persistência no modelo.
5. **A SPR-008B pode ser homologada?** Sim. Os critérios funcionais e
   arquiteturais da Sprint foram atendidos; a limitação da suíte legada é
   exclusivamente ambiental e está documentada.

## Declaração

**SPR-008B CONCLUÍDA**
