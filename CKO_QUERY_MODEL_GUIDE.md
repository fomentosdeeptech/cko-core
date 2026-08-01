# CKO Knowledge Query Foundation — Guia do Modelo

## Intenção

Uma consulta canônica registra o que deve ser selecionado, sem determinar como a seleção será realizada. Nenhum modelo contém plano de execução, expressão SQL, linguagem de grafo, consulta de motor de busca ou detalhe de armazenamento.

## Dimensões oficiais de filtro

As raízes aceitas são `identity`, `namespace`, `type`, `category`, `author`, `origin`, `version`, `status`, `created_at`, `modified_at`, `temporal`, `tags`, `keywords`, `attributes` e `properties`.

Filtros de atributos e propriedades exigem um caminho nomeado após a raiz. Filtros temporais exigem datetime consciente de fuso e são normalizados para UTC.

## Restrições

Operadores comparativos pertencem a `QueryConstraint`. `BETWEEN` exige limite inferior e superior do mesmo tipo, comparáveis e ordenados. `IN` exige sequência não vazia. `STARTS_WITH` e `ENDS_WITH` exigem texto. Operadores lógicos não são aceitos em restrições.

## Expressões

Operadores AND e OR exigem ao menos duas cláusulas. NOT exige exatamente uma cláusula. Cláusulas podem ser filtros ou expressões. Cláusulas repetidas e filtros repetidos entre a lista direta e a expressão são rejeitados.

## Ordenação

Cada ordenação declara campo, direção e prioridade inteira não negativa. Campos e prioridades devem ser únicos no descritor. A prioridade é declarativa e não aciona algoritmo de ordenação.

## Projeção

A projeção registra campos únicos e flags explícitas de inclusão de identidade e metadados. Ela não transforma objetos e não remove conteúdo durante esta Sprint.

## Paginação

O limite deve ser maior que zero. O deslocamento deve ser não negativo. Cursor lógico e deslocamento não zero são mutuamente exclusivos. O cursor não representa posição física ou token de tecnologia externa.

## Identidade e metadados

`QueryIdentity` associa UUID lógico, UUID canônico determinístico, namespace, nome e versão semântica. `QueryMetadata` registra criação, modificação, autor, estado, tags e atributos. Consultas canônicas aceitam estados DRAFT e READY.

## Resultados

`QueryResult` recebe itens já produzidos por uma camada externa. O modelo valida tipo, alvo declarado, unicidade, total esperado, total retornado, tempo lógico, estatísticas, avisos e metadados. Estados de resultado são COMPLETED, PARTIAL, EMPTY e FAILED. EMPTY não aceita itens.

O total retornado deve corresponder à quantidade de itens. O total esperado, quando presente, não pode ser menor que o total retornado. Os valores repetidos em `QueryStatistics` devem corresponder aos campos diretos do resultado.

## Coleções

`QueryCollection` contém consultas canônicas com identidades canônicas únicas. A coleção é iterável, possui comprimento e permanece imutável.

## Extensão futura

Uma camada futura poderá interpretar os modelos mediante um contrato próprio. Essa camada não deverá alterar a semântica, o schema, os discriminadores ou o formato canônico definidos pela SPR-014.
