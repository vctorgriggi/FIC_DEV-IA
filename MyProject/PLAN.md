# PLAN.md

> Plano de execução do LicitaLens (SPEC.md), fatiado em 10 fases pequenas e
> revisáveis, na ordem que a arquitetura pede: fundação executável primeiro;
> um corte vertical simples (perfil) para cravar o padrão das camadas; depois
> o pipeline de ingestão em fatias cuja lógica pura chega testada antes de
> qualquer borda; tudo que depende de LLM nasce atrás de fakes (a suíte nunca
> exige chave); UI por último porque só consome a API; demo e documentação de
> estudo fecham contra os critérios do SPEC.

## Convenções

- Cada task tem: um id (ex.: T2.1), o módulo responsável (coerente com a
  estrutura do CLAUDE.md), os testes TDD que a definem (ou a verificação, para
  infra/docs) e os critérios de aceitação.
- Uma fase só começa quando todos os checkboxes da anterior estão marcados.
- Gate de fase: ao final de cada fase rodam `uv run pytest`,
  `uv run ruff check .`, `uv run ruff format --check .` e `uv run pyright`;
  falhas são corrigidas antes de avançar (SPEC, critério 10).
- Toda borda externa (parser, storage, embeddings, LLM, banco, relógio) entra
  atrás de um port com fake determinístico; o adapter real chega na mesma fase
  ou depois, nunca antes do port.
- Nenhum teste toca rede (SPEC, constraint 6); integração usa um banco SQLite
  real em arquivo temporário, marcada com `pytest.mark.integration`.
- Convenções decididas durante a implementação são registradas no CLAUDE.md no
  ato; decisões arquiteturais ganham ADR em `docs/decisions/` no momento em
  que acontecem.
- Desvios são registrados na própria tarefa: o que mudou e por quê ficam no
  texto dela.

## Fase 0 — Fundação

Objetivo: esqueleto executável — app sobe, banco migra, gates e CI verdes.
Depende de: nada.

- [ ] T0.1 — Projeto uv + pyproject completo · módulo: raiz
  - Verificação: `uv sync --all-groups` instala; `uv run python -c "import licitalens"` funciona.
  - Aceitação: dependências do SPEC §Stack em grupos (main/dev); config de
    Ruff (lint + format + isort), Pyright (strict em `src/`), pytest
    (markers `integration`) e coverage no pyproject; `.python-version` = 3.14;
    `uv.lock` versionado; layout `src/licitalens/` criado com os pacotes vazios.
- [ ] T0.2 — Settings com pydantic-settings · módulo: core
  - Testes (primeiro): carrega de env; defaults documentados
    (`DATABASE_URL=sqlite+aiosqlite:///data/licitalens.db`,
    `MAX_UPLOAD_SIZE_MB=25`, `EMBEDDING_DIMENSION=1024`,
    `LLM_PROVIDER=fake`, `EMBEDDING_PROVIDER=fake`); provider real
    selecionado sem a respectiva API key falha cedo com mensagem apontando a
    variável.
  - Aceitação: `Settings` cobre APP_ENV, DATABASE_URL, LLM_PROVIDER,
    LLM_MODEL, LLM_API_KEY, EMBEDDING_PROVIDER, EMBEDDING_MODEL,
    EMBEDDING_API_KEY, EMBEDDING_DIMENSION, MAX_UPLOAD_SIZE_MB, STORAGE_PATH,
    LOG_LEVEL; `.env.example` espelha os nomes sem nenhum valor real.
- [ ] T0.3 — Logging estruturado + request id · módulo: core + presentation/api
  - Testes: entrada de log carrega `request_id` propagado por contextvars;
    filtro impede chave de API em log (teste com settings falsos).
  - Aceitação: structlog configurado (JSON em prod, legível em dev);
    middleware gera/propaga `X-Request-ID`.
- [ ] T0.4 — Alembic baseline + engine async SQLite · módulo: infrastructure/database
  - Testes (integração): `upgrade head` e `downgrade base` num banco limpo em
    arquivo temporário; PRAGMAs ativos em toda conexão (`journal_mode=WAL`,
    `foreign_keys=ON`).
  - Aceitação: `alembic.ini` + `migrations/` na raiz; env.py deriva a URL
    síncrona (`sqlite:///`) do settings; sessão async
    (`sqlite+aiosqlite:///`) com factory própria; migrations usam
    `batch_alter_table` onde o SQLite exigir (portabilidade p/ Postgres
    pós-MVP).
- [ ] T0.5 — App factory + `GET /health` + handlers base · módulo: presentation/api
  - Testes: 200 com status do banco; erro interno responde envelope
    consistente sem stack trace.
  - Aceitação: `create_app()`, exception handlers centrais (erro de domínio →
    HTTP), OpenAPI publicada.
- [ ] T0.6 — CI GitHub Actions · módulo: raiz
  - Verificação: workflow executa localmente os mesmos comandos do gate.
  - Aceitação: job único, sem serviços externos (SQLite dispensa service),
    rodando lint → format-check → pyright → pytest; cache de uv.
- [ ] T0.7 — ADRs fundacionais · módulo: docs
  - Verificação: leitura cruzada com SPEC (sem contradição).
  - Aceitação: `docs/decisions/` com 0001 monólito modular, 0002 SQLite
    primeiro com PostgreSQL+pgvector planejado (incl. busca exata vs ANN e
    psycopg vs asyncpg para quando o Postgres chegar), 0003 LangGraph (incl.
    por que mora em application), 0004 FastAPI, 0005 Streamlit, 0006
    abstração de provedores, 0007 sem OCR no MVP — curtos (contexto, decisão,
    consequências).

## Fase 1 — Perfil de empresa

Objetivo: primeiro corte vertical completo; vira o exemplo canônico do padrão
entidade → port → repositório → use case → rota.
Depende de: Fase 0 completa.

- [ ] T1.1 — Entidade `CompanyProfile` · módulo: domain/entities
  - Testes (primeiro): criação válida com defaults (listas vazias); `name`
    obrigatório; `created_at`/`updated_at` UTC vindos do port `Clock`.
  - Aceitação: entidade sem dependência de framework; `Clock` definido em
    domain/ports com fake em testes.
- [ ] T1.2 — Port `CompanyProfileRepository` + adapter SQLAlchemy · módulo: domain/ports + infrastructure/repositories
  - Testes (integração): add/get/update roundtrip; get inexistente retorna
    `None`; mapper converte model ↔ entidade sem vazar tipo SQLAlchemy.
  - Aceitação: model em infrastructure/database, mapper explícito, repositório
    específico (sem GenericRepository).
- [ ] T1.3 — Use cases create/get/update/list + DTOs · módulo: application/use_cases
  - Testes (primeiro): unit com repositório fake em memória; inexistente
    levanta `CompanyProfileNotFound` (domain/exceptions); list pagina
    (limit/offset).
  - Aceitação: um use case por arquivo; DTOs de entrada/saída próprios.
- [ ] T1.4 — Rotas `/company-profiles` (POST, GET, PUT, GET lista) · módulo: presentation/api
  - Testes: 201/200/404/422; erro de domínio mapeado por handler central;
    schema de resposta não expõe campos internos.
  - Aceitação: schemas request/response em presentation/api/schemas;
    composição em dependencies.

## Fase 2 — Upload e persistência do documento

Objetivo: PDF entra com validação, dedup e status confiáveis.
Depende de: Fase 1 completa.

- [ ] T2.1 — Entidade `Document` + máquina de status · módulo: domain/entities
  - Testes (primeiro): transições válidas (`UPLOADED→PROCESSING→PROCESSED|FAILED`);
    re-disparo permitido de qualquer status exceto `PROCESSING`; transição
    inválida levanta exceção; `processed_at` só em `PROCESSED`.
  - Aceitação: enum `DocumentStatus`; `content_hash` como value object.
- [ ] T2.2 — Port `DocumentStorage` + adapter local · módulo: domain/ports + infrastructure/storage
  - Testes: caminho derivado do hash (nunca do nome original); nome malicioso
    (`../../x.pdf`) não influencia caminho; write/read roundtrip; delete
    idempotente.
  - Aceitação: raiz em `STORAGE_PATH`; I/O síncrono encapsulado no adapter.
- [ ] T2.3 — Port `DocumentRepository` + adapter · módulo: domain/ports + infrastructure/repositories
  - Testes (integração): unique em `content_hash`; busca por hash e por id;
    list paginada.
  - Aceitação: migration dos campos do SPEC §Análise (Document).
- [ ] T2.4 — Use case `UploadDocument` · módulo: application/use_cases
  - Testes (primeiro): não-PDF (magic bytes) rejeitado; acima de
    `MAX_UPLOAD_SIZE_MB` rejeitado; duplicata retorna existente com flag;
    sucesso persiste `UPLOADED` + arquivo no storage (fake de storage nos
    units).
  - Aceitação: pipeline validar → hash → dedup → armazenar → persistir;
    falha de storage não deixa registro órfão (transação/compensação).
- [ ] T2.5 — Rotas `POST /documents`, `GET /documents/{id}`, `GET /documents` · módulo: presentation/api
  - Testes: multipart; 201 novo / 200 duplicata (SPEC, critério 2); 413/422
    para tamanho/tipo (critério 3); GET expõe status e `processing_error`.
  - Aceitação: upload validado na borda antes de ler o corpo inteiro quando
    possível (limite de tamanho).

## Fase 3 — Parsing e chunking

Objetivo: texto página a página, normalizado e chunkeado deterministicamente;
fixture de edital pronta para as fases seguintes.
Depende de: Fase 2 completa.

- [ ] T3.1 — Edital sintético + gerador · módulo: scripts + tests
  - Verificação: `uv run python scripts/make_fixture_pdf.py` gera PDF
    determinístico multi-página.
  - Aceitação: seções realistas (órgão, objeto, modalidade, valor estimado,
    prazos, habilitação jurídica/técnica/financeira, obrigações, penalidades)
    - 1 parágrafo com tentativa de prompt injection; conteúdo mora como texto
      no script (diff-ável); PDF com camada de texto extraível.
- [ ] T3.2 — Port `DocumentParser` + adapter PyMuPDF · módulo: domain/ports + infrastructure/documents
  - Testes: páginas da fixture com numeração correta (1-based); PDF sem
    camada de texto → `UnparseablePdf` com mensagem clara (SPEC, constraint
    1); assinatura recebe bytes/handle do storage — nunca caminho vindo do
    usuário.
  - Aceitação: retorna `ParsedPage(number, text)`; `page_count` preenchido no
    Document.
- [ ] T3.3 — Normalização de texto · módulo: application/services
  - Testes (primeiro): colapsa espaços e hifenização de quebra de linha;
    preserva números, datas, valores monetários e pontuação relevante (casos
    tabelados da fixture).
  - Aceitação: função pura, sem I/O, propriedade: normalizar duas vezes ==
    normalizar uma.
- [ ] T3.4 — Chunker · módulo: application/services
  - Testes (primeiro): janelas por caracteres com overlap configurável; corte
    preferencial em parágrafo/sentença; **nunca cruza página** (SPEC,
    constraint 9); `chunk_index` sequencial por documento; determinístico.
  - Aceitação: função pura; parâmetros (tamanho/overlap) em constantes
    documentadas.
- [ ] T3.5 — `DocumentChunk` + persistência do parse · módulo: domain/entities + infrastructure/repositories + application/use_cases
  - Testes (integração): chunks persistidos com `page_number`, `chunk_index`,
    `content`, `metadata`; reprocessar substitui os chunks anteriores na mesma
    transação.
  - Aceitação: migration de `document_chunks` (coluna `embedding` BLOB
    float32, nullable até a Fase 4).

## Fase 4 — Embeddings e busca

Objetivo: chunks viram vetores pesquisáveis; busca por similaridade provada
com fakes.
Depende de: Fase 3 completa.

- [ ] T4.1 — Port `EmbeddingProvider` + fake determinístico · módulo: domain/ports + infrastructure/embeddings
  - Testes (primeiro): mesmo texto → mesmo vetor; textos diferentes → vetores
    diferentes; dimensão = `EMBEDDING_DIMENSION`; batch preserva ordem.
  - Aceitação: fake baseado em hash do texto, normalizado (produção de teste,
    não mock ad hoc).
- [ ] T4.2 — Adapter Voyage (httpx) · módulo: infrastructure/embeddings
  - Testes: unit com `httpx.MockTransport` — sucesso, 429/5xx com retry
    limitado e backoff, timeout → erro tipado; header de auth nunca logado.
  - Aceitação: erros tipados compartilhados com o adapter de LLM
    (infrastructure/llm/errors.py ou módulo comum); sem SDK extra.
- [ ] T4.3 — `VectorSearchRepository` com busca exata · módulo: infrastructure/database + infrastructure/repositories
  - Testes (integração): grava embeddings normalizados como BLOB float32;
    top-k por cosseno (`math.sumprod` sobre `array('f')`) retorna o chunk
    esperado usando o fake; filtro por `document_id`; k e mínimo de
    similaridade parametrizáveis; escrita com dimensão ≠
    `EMBEDDING_DIMENSION` rejeitada.
  - Aceitação: busca exata em memória, O(chunks do documento) (SPEC,
    constraint 5); dimensão lida do settings num único lugar; port pronto
    para o adapter pgvector pós-MVP.
- [ ] T4.4 — Use case de indexação integrado · módulo: application/use_cases
  - Testes: parse → normalize → chunk → embed → persist ponta a ponta com
    fakes (sem LLM ainda); idempotente sob reprocessamento.
  - Aceitação: duração e contagem de chunks logadas (SPEC §observabilidade).

## Fase 5 — Extração estruturada e workflow

Objetivo: pipeline completo de análise com evidência validada e política
anti-injection, rodando inteiro com fakes.
Depende de: Fase 4 completa.

- [ ] T5.1 — Port `LLMProvider` + erros tipados + fake · módulo: domain/ports + infrastructure/llm
  - Testes (primeiro): contrato — recebe tarefa tipada (extração / resposta /
    relatório) com contexto e schema, devolve instância validada; fake
    determinístico responde a partir de roteiros por tarefa; erro de schema no
    fake explode alto (nunca silencioso).
  - Aceitação: nenhuma chamada a LLM fora deste port (grep no CLAUDE §Nunca
    fazer).
- [ ] T5.2 — Adapter Anthropic · módulo: infrastructure/llm
  - Testes: unit com client mockado — `messages.parse()` com schema Pydantic,
    timeout e retry limitado, mapeamento para erros tipados (rate limit,
    timeout, resposta inválida); log registra provedor/modelo/duração e nunca
    conteúdo integral de prompt/documento.
  - Aceitação: modelo default `claude-opus-5` via settings; adapter é borda
    fina (verificação manual roteirizada com chave real fica documentada na
    tarefa, fora da suíte).
- [ ] T5.3 — Schemas de extração com evidência · módulo: application/dto + domain/value_objects
  - Testes (primeiro): todo campo extraído exige `value + confidence +
pages + excerpt` ou `not_found=true` explícito; datas → date/datetime UTC
    e valores → Decimal preservando `raw_text`; enums (`BiddingModality`,
    categorias de requisito) com fallback `OTHER` explícito, nunca invenção.
  - Aceitação: `Evidence` como value object no domínio; schemas de LLM em
    application/dto (contrato com o modelo, não entidade).
- [ ] T5.4 — Nós determinísticos · módulo: application/workflows + domain/services
  - Testes (primeiro): `validate_evidence` — excerpt inexistente na página
    citada (comparação normalizada) rebaixa o campo a não localizado com
    flag de auditoria; cálculos de prazo (dias até submissão/abertura) e
    ordenações em Python puro; listas comparadas com normalização de
    caixa/acentos.
  - Aceitação: nenhum desses cálculos passa pelo LLM (SPEC, constraint 3).
- [ ] T5.5 — Grafo LangGraph + política anti-injection · módulo: application/workflows
  - Testes: estado tipado completo ao fim (`retrieve_context →
extract_tender_data → validate_evidence → analyze_company_eligibility →
identify_risks → build_checklist → review → generate_report`); com a
    fixture de injeção, a saída não obedece à instrução embutida nem contém
    prompt/segredos (SPEC, critério 7); conteúdo do edital sempre entra
    delimitado como dado; nós de eligibility/checklist são pulados sem
    perfil.
  - Aceitação: prompts como constantes versionadas em um módulo único; etapa
    `review` valida consistência antes do relatório.
- [ ] T5.6 — `TenderAnalysis` + processamento assíncrono · módulo: domain/entities + infrastructure/repositories + presentation/api
  - Testes (integração): `POST /documents/{id}/process` (com
    `company_profile_id` opcional) agenda BackgroundTask; status transita
    `PROCESSING → PROCESSED`; falha de workflow → `FAILED` +
    `processing_error` + rollback da análise parcial; reprocessar cria nova
    análise preservando anteriores; `GET /documents/{id}/analysis` retorna a
    mais recente (404 antes da primeira).
  - Aceitação: pipeline inteiro (fases 2–5) roda com fakes no edital
    sintético (SPEC, critério 5).

## Fase 6 — Perguntas com citações

Objetivo: RAG com resposta groundada, citações validadas e ausência honesta.
Depende de: Fase 5 completa.

- [ ] T6.1 — Use case `AskQuestion` · módulo: application/use_cases
  - Testes (primeiro): reformulação de consulta (determinística no fake);
    recuperação restrita ao documento; resposta cita apenas chunks
    recuperados; citações passam pelo mesmo validador de evidência de T5.4;
    `chunk_id`, `page` e `excerpt` consistentes entre si.
  - Aceitação: contrato de resposta do SPEC §RAG.
- [ ] T6.2 — Caminho `insufficient_context` · módulo: application/use_cases
  - Testes (primeiro): pergunta sem lastro → `insufficient_context=true`,
    zero citações, resposta informando ausência e o que seria necessário;
    citação inventada pelo LLM (simulada no fake) é descartada e rebaixa a
    confiança.
  - Aceitação: nunca inventa (SPEC, critério 6).
- [ ] T6.3 — Rota `POST /documents/{id}/questions` · módulo: presentation/api
  - Testes: 409 para documento não processado; injeção via campo de pergunta
    tratada como dado; contrato JSON exato do SPEC.
  - Aceitação: quantidade de chunks recuperados logada.

## Fase 7 — Comparação, checklist e relatório

Objetivo: exigências × perfil com veredito por item, checklist de pendências e
relatório final revisado.
Depende de: Fase 6 completa.

- [ ] T7.1 — Comparador determinístico · módulo: domain/services
  - Testes (primeiro): um caso por categoria — atendido / não atendido /
    precisa de confirmação / não localizado; matching com normalização de
    caixa/acentos; empate ambíguo cai em "precisa de confirmação" (nunca
    otimismo); requisito financeiro sem dado do perfil → precisa de
    confirmação.
  - Aceitação: entrada = requisitos extraídos + perfil; saída por item com
    referência à exigência de origem (com página); nenhum "apto/inapto"
    global.
- [ ] T7.2 — Checklist + rota · módulo: application/use_cases + presentation/api
  - Testes: deriva pendências da análise mais recente com perfil; sem perfil
    associado → 409 com mensagem orientando o `process` com
    `company_profile_id`; itens ordenados por criticidade determinística.
  - Aceitação: `GET /documents/{id}/checklist` (SPEC, critério 8).
- [ ] T7.3 — Relatório + rota · módulo: application/workflows + presentation/api
  - Testes: JSON agrega análise + comparação + riscos + pendências + limites
    ("não localizado no edital"); citações preservadas; render Markdown
    consistente com o JSON; nó `review` bloqueia relatório com evidência
    quebrada.
  - Aceitação: `GET /documents/{id}/report` em JSON e Markdown (SPEC,
    critério 9).

## Fase 8 — Interface Streamlit

Objetivo: demonstração completa consumindo só a API.
Depende de: Fase 7 completa.

- [ ] T8.1 — Cliente da API · módulo: ui
  - Testes: unit do `api_client` com `httpx.MockTransport` (contratos e
    erros); nenhum import de `licitalens` em `ui/` (teste de grep — SPEC,
    critério 12).
  - Aceitação: base URL configurável por env.
- [ ] T8.2 — Páginas · módulo: ui
  - Verificação: roteiro manual — selecionar/cadastrar empresa; enviar edital;
    acompanhar status (polling); ver resumo, requisitos, riscos; checklist;
    perguntar e ver citações (página + trecho); gerar/baixar relatório.
  - Aceitação: zero regra de negócio na UI; estados de erro da API exibidos
    com a mensagem da API.

## Fase 9 — Demo, documentação de estudo e fechamento

Objetivo: projeto estudável de ponta a ponta e critérios do SPEC fechados.
Depende de: Fase 8 completa.

- [ ] T9.1 — Seed e dados demo · módulo: scripts
  - Verificação: com API no ar, `uv run python scripts/seed.py` cria o perfil
    fictício, envia o edital sintético e dispara o processamento.
  - Aceitação: idempotente (rodar duas vezes não duplica).
- [ ] T9.2 — Perguntas e citações esperadas como e2e · módulo: tests
  - Testes: fixture `expected_qa` (pergunta → resposta esperada em substância
    - citações esperadas por página) roda contra o pipeline com fakes.
  - Aceitação: SPEC, critério 11.
- [ ] T9.3 — README · módulo: docs
  - Verificação: seguir o README numa máquina limpa (roteiro).
  - Aceitação: visão geral, arquitetura resumida, stack, como executar,
    variáveis, comandos, fluxo principal, exemplos de chamadas (curl) e
    decisões/limitações.
- [ ] T9.4 — docs/architecture.md · módulo: docs
  - Verificação: cada afirmação confere com o código (leitura cruzada).
  - Aceitação: responsabilidades por camada, direção das dependências,
    fluxos de upload/análise/pergunta, diagramas Mermaid, por que cada
    abstração existe, onde SOLID foi aplicado e onde deliberadamente evitamos
    abstração.
- [ ] T9.5 — docs/study-guide.md · módulo: docs
  - Verificação: roteiro do SPEC, critério 13.
  - Aceitação: ordem de estudo (entrada → rota → use case → ports → adapters →
    persistência → workflow → testes correspondentes); conceitos usados de
    Python, FastAPI, SQLAlchemy, RAG e agentes; 15 exercícios progressivos;
    perguntas de auto-verificação da arquitetura.
- [ ] T9.6 — docs/README.md + varredura de ADRs · módulo: docs
  - Verificação: todo documento de docs/ listado; decisões tomadas nas fases
    têm ADR.
  - Aceitação: mapa "o que mora onde" em uma página.
- [ ] T9.7 — Fechamento contra o SPEC · módulo: raiz
  - Verificação: executar os critérios de aceitação 1–13 do SPEC, um a um,
    registrando resultado na tarefa.
  - Aceitação: todos verdes; divergência vira correção antes do encerramento.

## Riscos e dependências

- **Saída do LLM fora do contrato** (SPEC, constraints 3 e 6) → T5.1–T5.3
  (parse com schema, evidência obrigatória) e T5.4 (`validate_evidence`).
  Plano B: retry único com o erro de validação anexado; persistindo, status
  `FAILED` com `processing_error` — nunca análise parcial sem evidência.
- **Prompt injection via edital** (SPEC, constraint 2) → fixture com injeção
  (T3.1), política e testes (T5.5, T6.3). Plano B: endurecer delimitação de
  contexto e reduzir superfície do prompt; injeção que passe vira caso de
  teste novo antes do fix.
- **Processamento em processo, sem fila** (SPEC, constraint 4) → T5.6 (status
  - re-disparo). Plano B assumido: documento preso em `PROCESSING` após
    restart exige re-disparo manual; fila real é pós-MVP (SPEC §Planejado).
- **Dimensão do embedding fixada e busca exata O(n)** (SPEC, constraint 5) →
  T4.3 (settings como fonte única; escala de um edital por consulta). Plano
  B: re-embed roteirizado ao trocar dimensão; pgvector/HNSW pós-MVP se a
  escala crescer.
- **SQLite single-writer** (SPEC, constraint 10) → T0.4 (WAL + foreign_keys);
  escrita concorrente restrita a request × BackgroundTask. Plano B:
  PostgreSQL planejado (SPEC §Planejado).
- **PDF sem camada de texto** (SPEC, constraint 1) → T3.2 (falha clara,
  `FAILED`). Plano B: nenhum — OCR é pós-MVP por decisão.
- **Fixture pouco realista contaminaria extração e QA** (SPEC, critérios 5, 6
  e 11) → T3.1 com seções reais de edital; T9.2 fecha o ciclo com respostas
  esperadas.
- **Citações página-fiéis vs. sentenças cruzando páginas** (SPEC, constraint 9) → T3.4 (chunk nunca cruza página; trade-off aceito e testado).

## Decisões em aberto

- [x] **Ordem das fases (perfil antes do pipeline)** — resolvido: corte
      vertical simples primeiro para cravar o padrão das camadas antes da
      complexidade do pipeline (proposta aprovada, 2026-08-04).
- [x] **Fakes como default de provider** — resolvido: `LLM_PROVIDER=fake` e
      `EMBEDDING_PROVIDER=fake` por default; afeta T0.2, T4.1, T5.1
      (2026-08-04).
- [x] **Sem Docker e sem Postgres no MVP** — resolvido: SQLite + aiosqlite e
      busca vetorial exata; Docker/Postgres/pgvector movidos para o pós-MVP
      do SPEC; afeta T0.4–T0.7 e T4.3 (revisão do usuário, 2026-08-04).

Nenhuma pendente.
