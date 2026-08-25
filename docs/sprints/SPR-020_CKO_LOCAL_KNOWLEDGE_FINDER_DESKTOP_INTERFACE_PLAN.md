# SPR-020 — CKO Local Knowledge Finder Desktop Interface Plan

## 1. Identificação, autoridade e estado

```text
SPRINT: SPR-020
PRODUCT: CKO Local Knowledge Finder Desktop Interface
TARGET_PLATFORM: Windows
STATUS: PLANNED / NOT AUTHORIZED FOR IMPLEMENTATION
GUI_IMPLEMENTATION_AUTHORIZED: NO
ARCHITECTURAL_DECISION_STATUS: PROPOSED / SUBJECT TO ARCHITECTURAL AUTHORIZATION
```

Este documento aloca e planeja a `SPR-020` sob o [índice canônico de Sprints](INDEX.md), com base na recuperação consolidada em [REV-008](../reviews/REV-008_CKO_LOCAL_KNOWLEDGE_FINDER_PILOT_RECOVERY_REVIEW.md). Não autoriza implementação, dependências, mudança de schema ou API pública.

## 2. Visão e fluxo operacional

Objetivo: permitir que uma pessoa selecione uma pasta, processe seu acervo documental, pesquise o conteúdo indexado, consulte proveniência, duplicatas e falhas e abra o documento de origem, sem precisar utilizar PowerShell.

Fluxo mínimo:

1. Abrir o aplicativo.
2. Selecionar uma pasta.
3. Confirmar onde o banco local será armazenado.
4. Iniciar o processamento.
5. Acompanhar o progresso.
6. Receber o resultado consolidado.
7. Pesquisar palavras ou expressões.
8. Ver resultados com título, trecho, tipo e localização.
9. Abrir o documento ou sua pasta no Explorador.
10. Consultar duplicatas, documentos sem texto e falhas.
11. Reprocessar a pasta quando necessário.

## 3. Requisitos funcionais

### 3.1 Configuração inicial

- Seletor nativo de pasta, com validação de existência e permissão de leitura.
- Banco automático no diretório de dados do usuário e opção avançada para outro local.
- Aviso explícito de que documentos originais não serão modificados.
- Confirmação adicional antes de processar uma pasta potencialmente ampla.

### 3.2 Processamento

- Ações `Processar pasta` e `Atualizar índice`.
- Progresso por etapa e contadores de descobertos, únicos, extraídos, indexados e não processados.
- Cancelamento seguro e cooperativo.
- Mensagens compreensíveis, com detalhes técnicos opcionais.
- Continuidade segura após falhas parciais e distinção inequívoca entre conclusão total e parcial.

### 3.3 Pesquisa

- Campo de pesquisa em destaque, acionado por botão ou Enter.
- Resultados ordenados por relevância, com termos destacados.
- Título ou nome do arquivo, trecho contextual, tipo, localização relativa, indicação de duplicata e estados de extração e indexação.
- Paginação ou carregamento progressivo.

### 3.4 Ações sobre resultados

- Abrir documento; abrir pasta no Explorador; copiar caminho.
- Consultar proveniência, todas as localizações de duplicatas e detalhes de processamento.
- Nunca alterar ou excluir automaticamente o arquivo original.

### 3.5 Relatórios

- Resumo da ingestão, duplicatas, falhas atuais, problemas históricos não resolvidos e documentos sem texto extraível.
- Linguagem compreensível ao usuário não técnico.
- Exportação futura será avaliada separadamente.

### 3.6 Estados e mensagens

A interface deve representar: aplicação sem pasta; pasta pronta; processamento em andamento; conclusão total; conclusão parcial; cancelamento; falha interna; banco indisponível; pasta removida ou desconectada; pesquisa vazia; e documento de origem não encontrado. Cada estado deve indicar a ação segura seguinte e nunca comunicar sucesso integral quando houver falha parcial.

## 4. Requisitos não funcionais

- Execução local, sem rede necessária para ingestão ou pesquisa, e privacidade por padrão.
- Documentos-fonte somente leitura; banco fora do repositório; logs sanitizados.
- Interface responsiva, operações longas em tarefa de fundo e cancelamento cooperativo.
- Compatibilidade inicial com Windows, caminhos Unicode e nomes com acentos.
- Suporte a unidades locais, externas e sincronizadas, com comportamento previsível quando desconectadas.
- Acessibilidade básica, navegação por teclado, contraste adequado e mensagens em português do Brasil.
- Empacotamento reproduzível e atualização sem perda do índice local.
- Recuperação segura após encerramento inesperado.

## 5. Arquitetura proposta

```text
Interface gráfica
→ camada de aplicação
→ serviços de descoberta, extração, indexação, pesquisa e relatórios
→ repositório SQLite
```

A interface deve reutilizar os serviços existentes por contratos internos estáveis ou por uma fachada de aplicação a ser definida em operação futura. Não deve conter SQL, reimplementar descoberta, extração ou indexação, interpretar tabelas internas, chamar PowerShell, usar análise da saída textual do CLI como integração principal ou modificar documentos de origem.

Responsabilidades propostas para a fachada: configuração validada, início e cancelamento de operações, eventos de progresso tipados, resultados e erros estruturados, consultas paginadas e ações seguras de abertura. A fachada é proposta, não autorizada.

## 6. Avaliação tecnológica

| Critério | Tkinter | PySide6 | Aplicação web local no navegador |
|---|---|---|---|
| Experiência Windows | Funcional, visual básico | Rica e consistente | Familiar, mas depende do navegador |
| Seletor nativo | Disponível | Disponível e robusto | Exige ponte local e sofre restrições do navegador |
| Acessibilidade | Básica, variável | Melhor suporte a foco, teclado e leitores | Boa base web, variável por navegador |
| Distribuição | Simples em dependências | Empacotamento maior | Requer servidor local e navegador |
| Tamanho do pacote | Menor | Maior | Médio a alto, conforme runtime |
| Dependências | Biblioteca padrão | Dependência externa relevante | Framework/servidor e frontend |
| Licença | Python/Tcl-Tk | LGPLv3/GPLv3/comercial; conformidade deve ser revisada | Depende da pilha escolhida |
| Atualização | Direta | Direta, com atenção ao runtime Qt | Duas camadas e superfície maior |
| Testes | Unitários e testes GUI limitados | Bom suporte unitário, integração e automação Qt | Ecossistema amplo de testes web |
| Integração Python | Direta | Direta | Requer API/IPC local |
| Manutenção | Baixa complexidade, menor riqueza | Boa estrutura para aplicação crescente | Maior complexidade operacional |
| Segurança | Superfície pequena | Superfície local controlável | Porta/servidor local e riscos de navegador |
| Operação totalmente local | Sim | Sim | Sim, com controles adicionais |

### 6.1 Decisão técnica proposta

`PySide6` é a recomendação técnica proposta. Oferece a melhor combinação de experiência nativa no Windows, acessibilidade, modelo de tarefas em segundo plano, widgets adequados para resultados e relatórios, testes e integração direta com os serviços Python. O custo é pacote maior e obrigação de revisar e cumprir a licença LGPLv3 ou adotar licença compatível.

Tkinter é a alternativa de contingência para um protótipo mínimo e de menor pacote, mas limita evolução visual e componentes. A aplicação web local não é preferida porque acrescenta servidor/IPC, superfície de segurança e integração indireta. Outras alternativas não apresentam justificativa objetiva suficiente neste escopo. A escolha final permanece `PROPOSED / SUBJECT TO ARCHITECTURAL AUTHORIZATION`; nenhuma dependência é adicionada nesta operação.

## 7. Wireframes textuais

### 7.1 Tela inicial e seleção de pasta

- Finalidade: configurar origem e banco.
- Componentes: cabeçalho, estado de privacidade, campo da pasta, `Selecionar pasta`, opção de banco automático/avançado e `Continuar`.
- Ações: selecionar, validar, trocar banco e confirmar pasta ampla.
- Estado vazio: instrução curta e botão principal.
- Erros: pasta ausente, inacessível ou banco inválido, com correção sugerida.
- Visível: caminhos escolhidos, disponibilidade e aviso de somente leitura.
- Oculto: conteúdo, hashes, detalhes internos do schema e rastros sensíveis.

### 7.2 Processamento e progresso

- Finalidade: acompanhar ingestão sem bloquear a interface.
- Componentes: etapa atual, barra, contadores, log resumido, `Cancelar` e detalhes expansíveis.
- Ações: cancelar cooperativamente, recolher detalhes e ir ao resultado.
- Estado vazio: aguardando início.
- Erros: conclusão parcial ou falha interna, sucessos preservados e próxima ação.
- Visível: métricas agregadas e mensagens sanitizadas.
- Oculto: conteúdo extraído, stack traces por padrão e caminhos completos desnecessários.

### 7.3 Pesquisa e lista de resultados

- Finalidade: localizar conteúdo indexado.
- Componentes: campo, filtros, lista paginada, snippets destacados e ordenação por relevância.
- Ações: pesquisar, filtrar, abrir detalhes, documento ou pasta.
- Estado vazio: orientação para pesquisar ou processar pasta.
- Erros: banco indisponível ou consulta inválida.
- Visível: título, trecho, tipo, localização relativa, duplicata e estado.
- Oculto: SQL, tabelas internas e conteúdo além do snippet necessário.

### 7.4 Detalhes do documento

- Finalidade: explicar origem e processamento.
- Componentes: título, tipo, localização relativa, estado, proveniência, outras localizações e ações.
- Ações: abrir, abrir pasta, copiar caminho e ver processamento.
- Estado vazio: origem não encontrada, mantendo registro histórico.
- Erros: unidade desconectada ou permissão negada.
- Visível: metadados operacionais necessários.
- Oculto: conteúdo integral, hash por padrão e internals do banco.

### 7.5 Duplicatas

- Finalidade: mostrar grupos e localizações sem deduplicação destrutiva.
- Componentes: resumo, grupos expansíveis e lista de localizações.
- Ações: abrir detalhes, arquivo ou pasta.
- Estado vazio: nenhuma duplicata identificada.
- Erros: localização ausente ou desconectada.
- Visível: contagens e localizações relativas.
- Oculto: conteúdo e comandos de exclusão.

### 7.6 Falhas e documentos sem texto

- Finalidade: separar falhas atuais, histórico não resolvido e `NO_TEXT`.
- Componentes: abas, filtros, motivo compreensível, detalhes opcionais e reprocessamento.
- Ações: inspecionar, localizar origem e reprocessar quando seguro.
- Estado vazio: mensagem positiva sem ocultar filtros ativos.
- Erros: reprocessamento indisponível ou origem ausente.
- Visível: classificação, estado, data e orientação.
- Oculto: conteúdo, exceção não sanitizada e inferência não comprovada sobre OCR.

### 7.7 Configurações

- Finalidade: controlar banco, comportamento e diagnóstico.
- Componentes: local do banco, idioma, aparência, logs, política de atualização e restauração de padrões.
- Ações: validar, salvar e escolher novo local com confirmação.
- Estado vazio: padrões seguros do usuário.
- Erros: diretório sem escrita ou banco incompatível.
- Visível: valores operacionais e consequências.
- Oculto: segredos, conteúdo indexado e opções destrutivas sem fluxo específico.

## 8. Estratégia de implementação futura

Os caminhos abaixo são somente propostas e deverão ser reconciliados com a árvore vigente antes de qualquer autorização.

### Incremento A — Fundação da interface

- Objetivo: criar shell, configuração local, seletor, inicialização do banco e ciclo de vida.
- Entregáveis: janela navegável, configuração persistente e validações.
- Aceitação: abre/encerra sem erro; seleciona pasta nativamente; banco fica fora do repositório.
- Testes: unidade de configuração, integração de inicialização, teclado e encerramento.
- Riscos: licença/empacotamento, caminhos Unicode e configuração inválida.
- Dependências: decisão arquitetural e tecnológica.
- Caminhos propostos: `packages/cko-local-finder/src/cko_local_finder/gui/`, `packages/cko-local-finder/tests/gui/` e configuração de empacotamento do pacote.

### Incremento B — Processamento

- Objetivo: integrar ingestão, progresso, cancelamento e estados total/parcial.
- Entregáveis: controlador assíncrono, eventos tipados e tela de progresso.
- Aceitação: interface responsiva; cancelamento seguro; sucessos indexados após falha parcial.
- Testes: unidade da fachada, integração sintética, cancelamento e injeção de falhas.
- Riscos: concorrência, encerramento inesperado e mensagem falsa de sucesso.
- Dependências: Incremento A e contratos de aplicação.
- Caminhos propostos: `application/` para fachada/casos de uso e `gui/` para apresentação, sem regras duplicadas.

### Incremento C — Pesquisa

- Objetivo: oferecer busca, snippets, abertura e proveniência.
- Entregáveis: busca paginada, lista, detalhes e ações do Explorador.
- Aceitação: pesquisa relevante; proveniência correta; abertura segura de arquivo/pasta.
- Testes: consultas sintéticas, paginação, Unicode, origem ausente e ação de abertura simulada.
- Riscos: exposição excessiva de caminho/conteúdo e bloqueio em consultas longas.
- Dependências: A, B e serviços existentes de pesquisa/proveniência.
- Caminhos propostos: adaptadores em `application/` e views/view-models em `gui/`.

### Incremento D — Relatórios

- Objetivo: apresentar ingestão, duplicatas, falhas, `NO_TEXT` e histórico.
- Entregáveis: painéis filtráveis e detalhes sanitizados.
- Aceitação: números consistentes com serviços; distinção clara entre falha e `NO_TEXT`.
- Testes: fixtures sintéticas, estados vazios, filtros e sanitização.
- Riscos: interpretação direta do schema e linguagem ambígua.
- Dependências: C e contratos de relatório.
- Caminhos propostos: consultas na fachada de `application/` e componentes em `gui/`.

### Incremento E — Empacotamento e piloto gráfico

- Objetivo: produzir instalador confiável e validar instalação, atualização e uso.
- Entregáveis: build reproduzível, instalador, estratégia de assinatura/confiança, guia e teste com usuário.
- Aceitação: instalação limpa; operação offline; atualização preserva índice; piloto gráfico aprovado.
- Testes: ambiente Windows limpo, upgrade, rollback/recuperação, antivírus e usabilidade/acessibilidade.
- Riscos: tamanho, reputação do executável, licença, migração acidental e perda de banco.
- Dependências: A–D, decisão de distribuição e política de atualização.
- Caminhos propostos: metadados de empacotamento do pacote, scripts dedicados futuros e documentação operacional; nenhum é criado agora.

## 9. Critérios de aceitação da futura interface

- Seleção por diálogo nativo e processamento completo sem PowerShell.
- Zero mutações dos documentos-fonte.
- Pesquisa funcional, resultados com proveniência e abertura do arquivo ou pasta.
- Duplicatas consultáveis e documentos sem texto identificáveis.
- Falha parcial comunicada corretamente, preservando o índice dos sucessos.
- Reprocessamento idempotente e banco preservado após atualização.
- Funcionamento sem internet e logs sem conteúdo sensível.
- Interface responsiva durante operações longas.
- Instalador validado em ambiente limpo.

## 10. Fora do escopo

- Nuvem, sincronização entre computadores, colaboração multiusuário ou servidor remoto.
- Autenticação corporativa, integração externa ou telemetria externa.
- Alteração, exclusão ou deduplicação destrutiva de documentos.
- OCR, salvo decisão posterior específica.
- Busca semântica com IA ou resumos automáticos.
- Interface móvel.
- Novo schema ou alteração da API pública do SDK.
- Qualquer implementação nesta operação documental.

## 11. Fundação compartilhada implementada — INC-GUI-001A

O `INC-GUI-001A` implementou a fachada interna tipada em `application/facade.py` e o
composition root compartilhado em `bootstrap.py`. O CLI passou a ser um adaptador fino
desse núcleo. A aplicação permanece independente de infraestrutura, CLI e apresentação;
o bootstrap conhece apenas aplicação, domínio e adaptadores concretos.

Foram introduzidos 13 eventos honestos de fronteira de etapa, sem percentuais, estimativas
ou cancelamento. A extração preserva sucessos persistidos e os indexa no fechamento do
lote mesmo quando uma falha inesperada posterior é propagada. Busca, proveniência,
relatórios, duplicatas, idempotência, formatos e códigos de saída do CLI permanecem
compatíveis.

Este incremento não criou GUI, não adicionou PySide6, não alterou dependências,
empacotamento, API pública, versão ou schema. A próxima implementação gráfica continua
dependente de autorização própria; `P-018-02` permanece não autorizado.

## 12. Gates para autorização futura

Uma operação posterior deverá aprovar tecnologia, licença, allowlist e incrementos. Deverá preservar `SDK 1.0.0`, API pública `646 / 646 / 646` com fingerprint `d47d3fea99b5773ec2eb97fce56d8f542211fb3104951f61b93f5265b16f9232`, Local Finder `0.1.0`, schema SQLite `3`, privacidade, idempotência e `P-018-02: NOT AUTHORIZED`.
