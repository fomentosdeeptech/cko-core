# CKO Document Canonical Model — Guia de Uso

## Fluxo oficial

O ciclo de criação começa pela composição de valores imutáveis de autoria, idioma, fonte, metadados, descritor e componentes opcionais. O agregado é sempre solicitado a `DocumentFactory.create`. A Factory cria a identidade canônica, especializa um Knowledge Object e valida o resultado.

Não se instancia `CanonicalDocument` nem `DocumentCollection` diretamente. A proteção é aplicada em tempo de execução por token privado da Factory.

## Definição da identidade

Quando `logical_id` não é informado, a Factory cria um `DocumentId`. Quando ele é informado, sua continuidade é preservada. `document_id` é sempre derivado do namespace e do identificador lógico.

Identidades físicas identificam manifestações, não caminhos ou arquivos. Identidades externas são um mapa imutável de esquemas nomeados para valores externos.

## Registro de origens

Todo documento canônico precisa de ao menos um `DocumentSource`. Múltiplas origens são aceitas desde que o par tipo e identificador seja único. A primeira origem fornece a proveniência primária usada na construção do Knowledge Object.

## Registro de representações

Cada manifestação física é declarada por `DocumentRepresentation`. Somente metadados técnicos são aceitos. Conteúdo binário, caminho, URL operacional, stream e lógica de leitura não pertencem ao modelo.

Quando há identidades físicas, deve haver representação correspondente no agregado. Hashes de representações não podem se repetir dentro do mesmo documento.

## Versão e Knowledge Object

A versão indicada por `DocumentMetadata.version` é usada tanto na versão documental inicial quanto na versão do Knowledge Object. O status documental é convertido para o estado homologado correspondente de Knowledge Objects.

Uma reconstrução com `from_parts` deve manter a última `DocumentVersion` alinhada aos metadados e ao Knowledge Object.

## Integridade

`DocumentIntegrity` requer SHA-256. Tamanhos lógico e físico são opcionais e não negativos. Assinatura é metadado textual opcional.

Status verificado exige indicador íntegro verdadeiro. Status de divergência exige indicador falso. Se metadados e integridade declaram checksum, os valores precisam coincidir.

## Estatísticas

Todos os contadores são opcionais. Valores fornecidos precisam ser inteiros não negativos. Ausência de valor significa informação não produzida; não significa zero.

## Serialização e intercâmbio

Use `DeterministicDocumentSerializer` para transporte e digest. Não monte envelopes manualmente. O serializer rejeita campos desconhecidos e JSON não canônico e reconstrói agregados pela Factory.

## Evolução

Consumidores devem verificar `schema_version` e usar apenas símbolos exportados por `cko.core.documents` ou pelo topo de `cko.core`. Novos schemas devem preservar discriminadores existentes ou fornecer migração explícita em Sprint futura.

## Restrições operacionais

O modelo não abre, lê, grava, move ou remove arquivos. Não inicia transações, não acessa rede, não persiste objetos e não executa extração. Essas responsabilidades permanecem fora do escopo documental canônico.
