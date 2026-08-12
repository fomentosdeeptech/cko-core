# ADR-001 — Federated Catalog Authority

**Processo:** CKO — ADR-001 — Federated Catalog Authority
**Status:** aceito
**Natureza:** decisão arquitetural; exclusivamente documental
**Ciclo:** Ciclo Arquitetural II
**Data:** 02/08/2026
**Decisão precedente:** CKO-ARCH-002 — Ecosystem Evolution Architecture
**Programa de execução:** CKO — GOV-002 — Cycle II Execution Program
**Baseline protegida:** CKO-BASELINE-2026.07
**SDK protegido:** `cko` 1.0.0
**API pública protegida:** 646 exports raiz, únicos e resolvidos
**Substitui:** nenhuma decisão anterior

> Primeiro ADR oficial do Ciclo Arquitetural II. Sua aprovação decide autoridade,
> ownership e fronteira do Catálogo Federado Institucional, mas não autoriza
> implementação, integração física, escrita, RFC, Sprint, alteração de contrato,
> API, SDK ou baseline.

## Controle normativo

**DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **PODE** e **RECOMENDADO** são termos
normativos. **Ativo** é algo passível de descrição por registro de catálogo; sua
inclusão não o incorpora ao Core, não transfere custódia e não o torna canônico.

## 1. Contexto

A CKO-BASELINE-2026.07 estabeleceu o CKO CORE SDK como núcleo compartilhado,
aplicações como consumidoras, infraestrutura como Adapters e governança como
autoridade institucional. A CKO-ARCH-002 adotou federação governada, composição
externa, Provenance by Design e Authority Stays at the Source. O GOV-002 definiu
como primeira decisão material a autoridade, o ownership e a fronteira do catálogo.

Sem esta decisão, federação poderia confundir descoberta com oficialização,
metadado com conteúdo, ownership com stewardship, confiança com canonicidade ou
agregação com transferência de autoridade. Poderia ainda criar, por conveniência,
um banco central, contrato do Core ou consulta que ampliasse acesso.

## 2. Decisão

Fica instituído o **Catálogo Federado Institucional da Plataforma CKO** como uma
camada lógica, governada e auditável de descoberta de ativos distribuídos.

O Catálogo é formado por **registros de catálogo** que descrevem, referenciam e
relacionam ativos mantidos sob autoridades de origem. Cada registro apresenta,
conforme classe e autorização, identidade, tipo, finalidade, owner, stewardship,
localização lógica, versão, estado, proveniência, confiança, restrições de acesso
e vínculo com a fonte.

O Catálogo:

- **é federado**, pois consulta ou agrega projeções autorizadas de fontes autônomas;
- **é institucional**, pois políticas, publicação e selo oficial são decididos
  pela governança competente;
- **é catálogo de referências e evidências**, não transferência de conteúdo,
  autoridade ou ownership;
- **é logicamente uno**, pois aplica políticas comuns, ainda que registros,
  projeções e índices permaneçam distribuídos;
- **é governado por estados explícitos**, sem promoção automática para confiável,
  curado ou oficial;
- **é read-only perante as fontes por padrão**; catalogação não autoriza mutação,
  sincronização bidirecional ou correção na origem.

Esta decisão define semântica e governança. NÃO define schema, endpoint,
protocolo, banco, índice, produto, pacote, namespace, biblioteca ou implantação.

## 3. Invariantes

1. Autoridade institucional permanece na fonte e nos órgãos competentes.
2. O registro não substitui o ativo, o original ou seu sistema de registro.
3. Inclusão no catálogo não significa incorporação ao Core.
4. Descoberta não significa validação; validação não significa publicação;
   publicação de metadados não significa publicação do conteúdo.
5. Identidades de origem são preservadas e conflitos permanecem explícitos.
6. Proveniência acompanha observação, transformação, decisão, publicação e consulta.
7. Acesso ao catálogo nunca amplia o acesso concedido pela fonte.
8. Confiança é multidimensional, explícita e dependente de evidência.
9. Ausência, conflito, restrição e descontinuação não são ocultados.
10. Aplicação, Adapter ou Provider não adquire autoridade por operar a federação.

## 4. Ativos elegíveis

Podem integrar o Catálogo, por registros descritivos e em escopo autorizado:

1. **capacidades públicas homologadas do Core**, sem copiar implementação ou
   criar exports;
2. **Aplicações**, jornadas, superfícies e capacidades declaradas;
3. **Adapters externos**, com tecnologia, fonte, limitações, versão, owner técnico
   e modos de falha;
4. **Providers externos**, com identidade, versão, escopo, owner, capacidades e
   limitações;
5. **Datasets** operacionais, transitórios, derivados, analíticos ou de
   intercâmbio, com finalidade e ciclo de vida delimitados;
6. **Corpora Institucionais**, suas coleções, versões, estados de curadoria e
   relações autorizadas;
7. **documentos, objetos de conhecimento, coleções, entidades, relações e
   evidências** pertencentes a Datasets ou Corpora, quando necessários e autorizados;
8. **taxonomias, vocabulários, CMCs, políticas e artefatos de governança**, como
   referências normativas, sem reduzir sua autoridade ao registro;
9. **projeções e derivados**, como resumos, índices, grafos, embeddings ou
   relatórios, identificados como derivados e vinculados às evidências originais;
10. **ativos legados**, sem implicar promoção, migração ou descontinuação.

O registro PODE conter somente o subconjunto mínimo permitido. A existência de
ativo sensível PODE permanecer não revelada quando até sua descoberta for restrita.

## 5. O que permanece fora do Catálogo

Permanecem fora da fronteira material e de autoridade do Catálogo:

- conteúdo original, salvo cópia futura autorizada por processo independente;
- bancos, diretórios, repositórios, Drive e demais sistemas de registro;
- credenciais, segredos, tokens, chaves e configuração sensível;
- autenticação, autorização, gestão de identidade e concessão de privilégios;
- decisões de canonicidade, taxonomia, confidencialidade, certificação, retenção,
  exclusão e validação humana;
- workflows, ingestão, movimentação, correção, exclusão, reclassificação ou
  sincronização;
- detalhes internos não pertencentes a superfície aprovada;
- dados pessoais, confidenciais ou regulados desnecessários à finalidade;
- observações sem direito de tratamento ou existência não revelável;
- resultados inferidos apresentados como fatos, fontes ou conhecimento oficial.

Esses elementos podem ser referenciados de forma protegida quando permitido, mas
não se tornam conteúdo governado pelo Catálogo.

## 6. Relação entre os papéis arquiteturais

| Papel | Relação com o Catálogo | Autoridade preservada |
|---|---|---|
| Core | Fornece apenas contratos, modelos e comportamentos públicos homologados. | Autoridade técnica sobre o SDK; nenhuma sobre conteúdo institucional. |
| Aplicação | Atua como composition root, seleciona Providers e Adapters, aplica políticas e apresenta jornadas. | Sua jornada e operação, dentro das políticas institucionais. |
| Adapter | Conecta tecnologia ou fonte e preserva identidade, limites e evidência técnica. | Nenhuma autoridade semântica decorrente da conectividade. |
| Provider | Expõe capacidade semântica e observações candidatas. | Nenhuma autoridade para promover observação a ativo oficial. |
| Dataset | É descrito e consultado conforme finalidade, schema, origem e ciclo de vida. | Owner mantém responsabilidade operacional; Dataset não é fonte institucional por si só. |
| Corpus Institucional | Tem escopo, itens, relações e estados publicados como conhecimento governado. | Autoridade aprovadora e steward mantêm curadoria e reconhecimento institucional. |

```text
fonte governada
  -> Adapter externo (conectividade)
  -> Provider externo (capacidade/observação)
  -> Aplicação (composição e política contextual)
  -> registro/projeção federada (identidade, proveniência e confiança)
  -> consulta autorizada

Governança decide política, admissão e publicação.
Core permanece neutro e não depende dos elementos externos.
```

## 7. Modelo de autoridade

A autoridade é distribuída por competência e NÃO é transferida ao operador:

| Competência | Autoridade responsável | Poder |
|---|---|---|
| Política do Catálogo | Governança Institucional | Aprovar política, estados, critérios e selo institucional. |
| Conteúdo, classificação e canonicidade | Autoridade da fonte ou domínio | Confirmar significado, legitimidade, correção e estado institucional. |
| Corpus Institucional | Autoridade aprovadora, com seu steward | Aprovar inclusão, exclusão, curadoria, publicação e descontinuação. |
| Dataset | Owner e autoridade de dados aplicável | Aprovar finalidade, qualidade declarada, ciclo de vida e uso. |
| Segurança, privacidade e direitos | Autoridades competentes | Autorizar, restringir ou bloquear descoberta, consulta e reutilização. |
| Exatidão técnica | Owner técnico de Aplicação, Adapter ou Provider | Atestar versão, capacidades, limites e evidências técnicas. |
| Operação do Catálogo | Custódia operacional designada | Operar projeções sem decidir canonicidade ou acesso. |
| Gate D5 | Governança, owners, stewards e autoridades afetadas | Homologar, restringir, corrigir ou retirar a federação. |

Segurança, privacidade, autoridade da fonte e autoridade do Corpus mantêm poder de
bloqueio em suas competências. Divergências permanecem visíveis e são encaminhadas
à autoridade competente, não resolvidas por maioria automática.

## 8. Modelo de ownership

Todo ativo catalogado DEVE possuir um **owner accountable** identificável. O
owner responde pela finalidade, legitimidade, ciclo de vida, qualidade declarada,
restrições e correção do ativo dentro de sua competência.

- Ownership do ativo permanece na fonte; catalogação não o transfere.
- Ownership de projeção ou derivado é próprio e não substitui o das entradas.
- Ownership técnico de Adapter ou Provider é distinto do conteúdo.
- Custódia operacional de arquivos, bancos ou catálogo é distinta de ownership.
- Coowners exigem responsabilidades e desempate formalmente definidos; caso
  contrário, DEVE existir um único owner accountable.
- Ativo sem owner não pode ser publicado; PODE permanecer em inventário restrito
  como pendência, se sua retenção for legítima e autorizada.

## 9. Modelo de stewardship

Stewardship é a responsabilidade delegada de manter contexto, metadados,
qualidade, taxonomia aplicada, revisões e propostas de correção. O steward:

- acompanha o ativo durante seu ciclo de vida;
- verifica metadados, proveniência, atualidade e conflitos;
- propõe inclusão, correção, restrição, retirada ou nova versão;
- coordena validação humana e registra evidências;
- NÃO substitui o owner nem a autoridade aprovadora;
- NÃO amplia acesso nem declara canonicidade fora de delegação expressa.

Corpus Institucional DEVE ter steward. Dataset publicado DEVE ter steward ou
função equivalente. Aplicações, Adapters e Providers DEVEM ter stewardship
técnico adequado ao ciclo de vida.

## 10. Política de identidade

A identidade possui camadas distintas:

1. **identidade do registro**, estável e opaca no escopo institucional;
2. **identidade qualificada na fonte**, composta pela autoridade/fonte e pelo
   identificador local, preservada sem reescrita;
3. **identidade da versão ou revisão**, para ativo temporal ou mutável;
4. **alegações de equivalência, derivação ou sucessão**, como relações explícitas,
   versionadas, atribuídas e sustentadas por evidência.

São regras obrigatórias:

- igualdade de nome, hash, caminho, título ou conteúdo NÃO prova identidade;
- resolução técnica NÃO autoriza fusão, deduplicação destrutiva ou canonicidade;
- conflitos, aliases e duplicidades permanecem representados até decisão;
- identificador preferencial não apaga identificadores de origem;
- mudança de localização não altera identidade lógica quando houver continuidade;
- reutilização de identificador para outro ativo é proibida;
- ativos sem identidade estável podem ser provisórios, com publicação limitada;
- identificadores sensíveis usam referência protegida ou pseudônimo governado.

Esta política não cria tipo, campo ou algoritmo no SDK e não decide o mecanismo
detalhado de reconciliação. Protocolo, schema ou automação exigirá instrumento
posterior próprio.

## 11. Política de proveniência

Proveniência é obrigatória em observação, transformação, decisão, publicação e
consulta relevante. Dentro dos contratos homologados, deve permitir determinar:

- ativo, fonte, localização lógica e versão observados;
- agente humano ou técnico responsável;
- atividade, instante e finalidade;
- entradas, parâmetros, políticas e transformações;
- resultado ou derivado;
- evidência de identidade, relação, confiança e validação;
- estado de publicação e autoridade decisora;
- regra de acesso aplicável.

Registros DEVEM ser imutáveis ou append-only, ordenáveis, serializáveis e
auditáveis. Correções geram nova declaração vinculada; não apagam a história.
Lacunas e conflitos ficam explícitos. Dados sensíveis não são copiados quando uma
referência protegida for suficiente.

## 12. Estados de catalogação e publicação

| Estado | Significado | Efeito permitido |
|---|---|---|
| Localizado | Observação inicial ainda não admitida. | Inventário restrito; sem publicação. |
| Registrado | Identidade mínima, owner, finalidade, acesso e proveniência aceitos. | Descoberta no perímetro autorizado. |
| Verificado | Metadados e vínculo com a fonte validados. | Consulta autorizada com limitações. |
| Curado | Steward concluiu revisão semântica aplicável. | Uso governado no contexto aprovado. |
| Oficial | Autoridade aprovou o estado institucional. | Selo oficial no escopo autorizado. |
| Restrito | Existência ou metadados exigem controle adicional. | Visibilidade somente a autorizados. |
| Suspenso | Risco, conflito, expiração ou incidente impede uso. | Retido para auditoria; consulta bloqueada. |
| Retirado | Publicação encerrada sem apagar histórico. | Tombstone ou referência histórica governada. |
| Rejeitado | Critérios de admissão não atendidos. | Não publicado; decisão preservada quando legítimo. |

Estados de maturidade e acesso são independentes: ativo oficial pode ser restrito,
e ativo público pode não ser oficial.

## 13. Critérios para inclusão

Um ativo somente passa de Localizado para Registrado quando houver:

1. aderência ao escopo e finalidade legítima;
2. autoridade da fonte, owner e steward/função equivalente identificados;
3. identidade de registro e de origem suficientes;
4. classe e relações com originais ou derivados declaradas;
5. proveniência mínima verificável;
6. direitos, licença, consentimento e base de tratamento adequados;
7. classificação de acesso e regra de consulta;
8. versão, temporalidade, atualização, retenção e retirada conhecidas;
9. qualidade, limitações, conflitos e confiança declarados;
10. metadados mínimos compatíveis com a descoberta;
11. aprovação do owner e das autoridades aplicáveis;
12. ausência de alteração implícita no Core, SDK, API ou baseline.

Isso permite inclusão do **registro**, não publicação do conteúdo nem
reconhecimento institucional do ativo.

## 14. Critérios para exclusão, bloqueio ou retirada

Um ativo DEVE ser rejeitado, suspenso ou retirado do perímetro publicado quando:

- não houver finalidade legítima, owner, autoridade ou direito suficiente;
- identidade ou proveniência forem insuficientes ao estado pretendido;
- sua presença violar confidencialidade, privacidade, licença ou retenção;
- metadados forem falsos, enganosos, desatualizados ou irreconciliáveis sem aviso;
- estiver comprometido, malicioso, corrompido ou sob incidente;
- publicação criar risco de inferência, enumeração ou acesso indevido;
- estiver fora do escopo ou duplicar registro sem relação explícita;
- o ciclo de vida encerrar ou a autoridade revogar publicação;
- a fonte não puder sustentar a evidência exigida.

Exclusão da publicação NÃO apaga a fonte nem a trilha. Registro mínimo de rejeição,
suspensão ou retirada só é preservado com base legítima e respeito a retenção,
privacidade e direito aplicável.

## 15. Critérios de confiança

Confiança NÃO é score único. DEVE ser avaliada por:

- autoridade e competência da fonte;
- completude e verificabilidade da proveniência;
- confiança da resolução de identidade;
- integridade e autenticidade da evidência;
- qualidade, cobertura e limitações;
- atualidade e validade temporal;
- validação humana e curadoria;
- direitos, finalidade e conformidade de acesso;
- consistência entre fontes e conflitos abertos.

| Nível | Condição mínima | Limite |
|---|---|---|
| T0 — Não avaliado | Observação sem evidência suficiente. | Não publicável. |
| T1 — Rastreável | Fonte e proveniência mínimas conhecidas. | Inventário restrito; não serve a decisão institucional. |
| T2 — Verificado | Identidade, integridade e metadados essenciais verificados. | Consulta autorizada, com limitações. |
| T3 — Curado | Steward validou contexto, qualidade e uso. | Uso governado no escopo aprovado. |
| T4 — Oficial | Autoridade aprovou estado institucional e vigência. | Oficial apenas no domínio, finalidade, versão e período declarados. |

Nenhum cálculo automático promove ativo. Conflito crítico, proveniência quebrada,
expiração ou incidente pode limitar uso ou suspender publicação.

## 16. Critérios de publicação

Há dois atos diferentes:

1. **publicar o registro:** tornar metadados autorizados descobríveis em certo
   perímetro;
2. **publicar conhecimento institucional:** atribuir estado Oficial por decisão
   da autoridade competente.

Publicar registro exige estado mínimo Verificado/T2, owner, steward aplicável,
proveniência, classificação de acesso, finalidade, versão, limitações, aprovações
e mecanismo de correção e retirada. Estado inferior só pode existir em inventário
restrito, claramente rotulado e autorizado.

Publicar conhecimento institucional exige ainda curadoria, validação humana,
direitos confirmados, vínculo com originais, política de inclusão/exclusão,
decisão registrada e estado Oficial/T4.

Toda publicação DEVE registrar escopo, audiência, instante, versão e decisão. Nova
versão não substitui silenciosamente a anterior. Retirada produz estado ou
tombstone auditável conforme acesso e retenção.

## 17. Critérios de consulta

Toda consulta federada DEVE:

- possuir identidade do consulente, finalidade e contexto de autorização;
- aplicar menor privilégio e interseção das políticas institucional, da fonte, do
  ativo e da aplicação;
- filtrar antes de revelar existência, metadados, contagens ou conteúdo;
- separar descoberta, visualização de metadados, acesso e reutilização;
- preservar restrições ao combinar fontes;
- apresentar fonte, versão, estado, confiança, limitações e Provenance;
- explicitar parcialidade, indisponibilidade, conflitos e instante de validade;
- produzir auditoria proporcional ao risco e à classificação;
- impedir que cache, índice, exportação ou projeção contorne revogação e retenção;
- evitar inferência de restritos por ordenação, facetas, erros ou métricas.

Consulta não concede reutilização, não valida conteúdo e não altera ativo. A fonte
pode negar ou limitar resposta. Implementação futura falha de forma segura quando
não puder determinar autorização.

## 18. Limites arquiteturais do Catálogo

O Catálogo NÃO é:

- data lake, banco canônico, repositório ou sistema de registro;
- master data management ou deduplicação destrutiva;
- autoridade de CMC, taxonomia, certificação ou canonicidade;
- IAM, cofre de segredos ou substituto das políticas das fontes;
- motor obrigatório de busca, grafo, embeddings, RAG ou IA;
- workflow de ingestão, curadoria, publicação, retenção ou exclusão;
- mecanismo de escrita ou sincronização bidirecional;
- novo módulo, namespace, contrato ou export do Core;
- justificativa para centralização, cópia, promoção ou fim do legado.

Este ADR não decide persistência, indexação física, protocolo, schema, interface,
SLA, tecnologia, topologia ou política institucional completa de retenção e
exclusão. Essas escolhas exigem evidência e instrumentos futuros.

## 19. Segurança, privacidade e rollback

- Descoberta segue menor conhecimento e menor privilégio.
- Políticas da fonte são piso, nunca teto ampliável pelo Catálogo.
- Registros sensíveis usam minimização, referências protegidas e separação.
- Logs e Provenance não reproduzem segredos ou conteúdo desnecessário.
- Revogação, expiração e mudança de acesso alcançam projeções e caches dentro de
  prazo futuramente definido pela autoridade competente.
- Integração futura deve desligar por fonte, Provider, Adapter, domínio e Aplicação
  sem afetar o original.
- Falha do Catálogo não autoriza bypass nem torna projeção fonte de verdade.

Não há migração ou rollback técnico imediato, pois a decisão é documental. Sua
reversão exige novo ADR, preservando histórico.

## 20. Impactos arquiteturais

### 20.1 Imediatos

- estabelece vocabulário, fronteira e invariantes;
- separa autoridade, ownership, stewardship e custódia;
- define condições para inventário, registro, confiança, publicação e consulta;
- fornece decisão material para as Ondas II.1–II.5;
- cria critérios verificáveis para D5 do GOV-002.

Os impactos imediatos são exclusivamente documentais. Não há modificação em
código, runtime, dados, contratos, API, SDK, builds, dependências, bancos,
empacotamento ou processos operacionais.

### 20.2 Futuros condicionais

RFCs e Sprints futuras, separadamente aprovadas, poderão especificar e executar
protocolo, schema, Adapters, Providers, composition roots, autorização, consulta,
observabilidade e conformidade. A implementação permanece externa ao Core até
eventual promoção formal e deve respeitar os 646 exports.

Aprovar este ADR não autoriza onda, não aprova D1–D5 e não dispensa pilotos,
evidências ou homologação.

## 21. Alternativas consideradas

### A. Catálogo central com cópia física

**Rejeitada.** Confunde catálogo e repositório, aumenta risco, duplica conteúdo,
enfraquece a fonte e antecipa persistência. Contraria Federation Before
Consolidation.

### B. Catálogo como módulo e autoridade do Core

**Rejeitada.** O Core é núcleo técnico neutro. A alternativa o acoplaria a fontes,
taxonomias, permissões e jornadas e poderia alterar contratos e os 646 exports.

### C. Catálogos independentes por Aplicação

**Rejeitada.** Fragmenta identidade, Provenance, confiança e acesso; favorece
duplicidade e impede consulta institucional governada.

### D. Provider ou Discovery como autoridade automática

**Rejeitada.** Provider produz observação candidata. Conectividade e resolução
técnica não substituem owner, steward, validação humana ou autoridade.

### E. Fonte técnica como única autoridade

**Rejeitada.** A fonte preserva autoridade sobre ativos, mas não decide sozinha
políticas transversais, equivalências entre domínios, selo ou acesso combinado.

### F. Score único e automático de confiança

**Rejeitada.** Um número oculta dimensões, contexto, conflitos e validade e pode
promover observação indevidamente.

### G. Não criar catálogo institucional

**Rejeitada.** Mantém silos, dificulta reutilização responsável e impede realizar
o Ciclo II com autoridade, Provenance e consulta auditáveis.

## 22. Justificativa

A federação lógica governada é a alternativa que combina descoberta transversal
com preservação das fontes, autoridades e controles. Permite reutilização antes
de consolidação física, mantém Core e API estáveis, torna conflitos e confiança
visíveis e separa observação técnica de reconhecimento institucional.

O modelo distribui decisões por competência: governança define política; owners
respondem pelos ativos; stewards mantêm contexto e qualidade; autoridades de
segurança e domínio controlam acesso e oficialização; Aplicações compõem jornadas;
Providers expõem capacidades; Adapters conectam fontes; o Core permanece neutro.

## 23. Consequências

### 23.1 Positivas

- descoberta institucional sem centralização obrigatória;
- autoridade, originais e legado preservados;
- ownership e stewardship rastreáveis;
- proveniência e confiança incorporadas à decisão;
- menor privilégio sem ampliação de acesso pela federação;
- evolução externa, incremental, reversível e compatível;
- base objetiva para D1, D2 e D5 e futuras especificações.

### 23.2 Custos e trade-offs

- coordenação entre owners, stewards e autoridades;
- consultas potencialmente parciais, lentas ou indisponíveis por fonte;
- gestão de versões, aliases, conflitos e tombstones;
- metadados menos uniformes e cobertura variável;
- presença no Catálogo não garante qualidade ou acesso;
- auditoria, revisão e revogação contínuas.

### 23.3 Riscos residuais

- deriva entre projeção e fonte;
- inferência de ativos restritos;
- owner ou steward indisponível;
- equivalências incorretas;
- interpretação de Verificado/Curado como Oficial;
- pressão por centralização ou promoção prematura.

Mitigações: autorização em tempo de consulta, Provenance append-only, estados
explícitos, revisões, isolamento, desligamento por trilha e gates do GOV-002.

## 24. Consequências futuras e decisões pendentes

Esta decisão permite especificar futuramente, se os gates provarem necessidade:

1. protocolo e perfil mínimo de registro;
2. mapeamentos por classe e fonte;
3. autorização entre domínios;
4. resolução detalhada de identidade e duplicidades;
5. composição de Adapters e Providers;
6. observabilidade, auditoria, SLOs e indisponibilidade;
7. retenção, exclusão e direito aplicável a registros e Provenance;
8. persistência ou índice físico, somente se a federação provar necessidade.

Cada item exige o instrumento previsto pelo GOV-002. Nenhum é autorizado aqui.

## 25. Compatibilidade

| Referência | Compatibilidade |
|---|---|
| ARCH-001 — CKO CORE SDK | Mantém monólito modular, Ports and Adapters, dependências para dentro, Core neutro, governança soberana e integrações externas. |
| CKO-ARCH-001 — Arquitetura Canônica | Preserva SDK compartilhado, aplicações consumidoras, infraestrutura substituível e decisões sob governança. |
| CKO-ARCH-002 | Decide fronteira, autoridade e ownership; aplica Federation Before Consolidation, Provenance by Design e Authority Stays at the Source. |
| CKO-GOV-001 | Preserva governança sobre catalogação, canonicidade, CMC, taxonomia, confidencialidade, certificação e validação humana. |
| GOV-002 | Satisfaz a precedência documental sem autorizar onda, RFC, Sprint ou implementação; mantém D0–D7. |
| SDK `cko` 1.0.0 | Não modifica módulo, namespace, dependência, comportamento, empacotamento ou versão. |
| API pública | Preserva os 646 exports; não cria, remove, renomeia, deprecia ou reinterpreta símbolo. |
| CKO-BASELINE-2026.07 | Não altera, reabre, substitui ou promove elemento à baseline. |
| Legado e originais | Permanecem nas fontes, com identidade, autoridade e reversibilidade. |
| Persistência | Não escolhe banco, índice, cache ou repositório e não autoriza cópia. |

Conclusão: decisão **compatível por construção**, pois atua apenas como política
de composição externa e sujeita mudanças executáveis a instrumentos posteriores.

## 26. Critérios de conformidade

Iniciativa conforme DEVE demonstrar:

- fronteira entre registro, projeção, conteúdo e fonte;
- autoridade, owner, steward e custódia identificados;
- identidade de origem preservada e conflitos explícitos;
- Provenance ponta a ponta e confiança multidimensional;
- estados de catalogação e publicação rotulados;
- autorização em tempo de consulta e nenhuma ampliação de acesso;
- leitura por padrão, minimização e reversibilidade;
- Core, SDK 1.0.0, 646 exports e baseline inalterados;
- instrumento posterior aprovado antes de implementação;
- evidência para o gate aplicável do GOV-002.

Não conformidade material impede publicação e homologação D5.

## 27. Declaração final

Fica decidido que o Catálogo Federado Institucional é camada lógica e governada
de registros, referências e evidências sobre ativos distribuídos. Preserva
conteúdo, identidade, ownership e autoridade nas fontes; usa Aplicações como
composition roots, Providers como expositores de capacidades, Adapters como
conectores e o Core apenas por sua API pública homologada.

Datasets permanecem coleções operacionais sem autoridade institucional intrínseca.
Corpora Institucionais permanecem coleções curadas, com steward e autoridade
aprovadora. Nenhuma inclusão, confiança, publicação ou consulta ocorre por mera
descoberta técnica.

Esta decisão não implementa código, não altera contratos, API, SDK ou baseline,
não cria RFC ou Sprint e não autoriza escrita, migração, centralização, promoção
ou descontinuação. Execução futura depende dos gates e instrumentos do GOV-002.

## Referências

- [ARCH-001 — CKO CORE SDK](../../ARCH-001_CKO_CORE_MASTER_ARCHITECTURE.md)
- [CKO-ARCH-001 — Arquitetura Canônica](../../../docs/arquitetura/CKO-ARCH-001_ARQUITETURA_CANONICA.md)
- [CKO-ARCH-002 — Ecosystem Evolution Architecture](../arquitetura/CKO-ARCH-002_ECOSYSTEM_EVOLUTION_ARCHITECTURE.md)
- [CKO-GOV-001 — Baseline Arquitetural 1.0](../../../docs/governance/CKO-GOV-001_BASELINE_ARQUITETURAL_1.0.md)
- [GOV-002 — Cycle II Execution Program](../governance/GOV-002_CYCLE_II_EXECUTION_PROGRAM.md)
- [Política de Decisões Arquiteturais](../../../docs/governance/ARCHITECTURE_DECISIONS.md)
- [Índice de ADRs](INDEX.md)
