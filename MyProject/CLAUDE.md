# LicitaLens

> Plataforma de análise inteligente de editais de licitação: ingere PDF
> textual, extrai informações estruturadas com evidência por página, compara
> com o perfil da empresa, responde perguntas com citações e gera relatório.
> Monólito modular em Python, construído como material de estudo.

Leia este arquivo no início de toda sessão — ele é o **contrato de como
escrevemos código aqui**, não documentação. Quando uma convenção for decidida
durante a implementação, registre-a aqui (e, se for decisão arquitetural, em
`docs/decisions/`). Contexto detalhado mora em @SPEC.md (o quê e por quê) e
@PLAN.md (ordem de execução).

**Fase atual = Fase 0 (nada implementado ainda).** O escopo é o MVP do SPEC;
tudo na seção "Planejado / pós-MVP" do SPEC (OCR, auth, multi-tenant, fila
real) não deve ser implementado nem parcialmente antecipado.

## Regra de ouro

**Nenhuma informação sobre o edital sai do sistema sem evidência verificável
(página + trecho conferido contra o texto) ou marcação explícita de
ausência.** Tudo abaixo é desdobramento disso.

Na prática: o LLM propõe, a validação determinística dispõe. Todo campo
extraído e toda citação de resposta carregam `page` + `excerpt` que o
`validate_evidence` confere contra o texto real da página (match normalizado);
o que não bate é rebaixado a "não localizado" — nunca aceito em silêncio. O
schema Pydantic exige evidência ou `not_found=true`; não existe terceiro
estado. Ausência é resposta válida e obrigatória: inventar preenchimento é o
único bug sem conserto retroativo, porque contamina dados persistidos.

A segunda disciplina, estrutural: **dependências apontam para dentro** —
`domain` não importa nada de fora; `application` importa só `domain` (exceção
única e deliberada: `langgraph` em `application/workflows`, ADR 0003);
FastAPI, SQLAlchemy, Streamlit e SDKs vivem em `infrastructure`/`presentation`
/`ui` e entram no núcleo apenas via ports.

## Stack

| Camada        | Tecnologia                                                          |
| ------------- | ------------------------------------------------------------------- |
| Linguagem     | Python 3.14 (uv gerencia projeto, deps e lockfile)                  |
| API           | FastAPI ≥ 0.141, Pydantic ≥ 2.13, pydantic-settings ≥ 2.14          |
| Persistência  | SQLite (aiosqlite) + SQLAlchemy 2 async + Alembic; Postgres pós-MVP |
| Workflow      | LangGraph ≥ 1.2 (estado tipado, um agente, nós determinísticos)     |
| LLM           | anthropic SDK (default `claude-opus-5`) atrás de `LLMProvider`      |
| Embeddings    | Voyage via httpx atrás de `EmbeddingProvider` (dim 1024)            |
| PDF           | PyMuPDF ≥ 1.28                                                      |
| UI demo       | Streamlit ≥ 1.61 (consome a API; não importa `licitalens`)          |
| Observability | structlog (JSON em prod; contextvars p/ request_id/document_id)     |
| Qualidade     | pytest (+asyncio, +cov), Ruff (lint+format), Pyright strict         |

## Estrutura

Os caminhos abaixo são os nomes canônicos de módulo usados nas tarefas do
PLAN.md (`· módulo:`).

```
raiz                          # pyproject.toml, uv.lock, .github/, data/ (SQLite; fora do git)
src/licitalens/
  domain/                     # núcleo puro: zero import de framework
  domain/entities/            # CompanyProfile, Document, DocumentChunk, TenderAnalysis
  domain/value_objects/       # Evidence, Money, Confidence, enums (status, modalidade)
  domain/services/            # regras determinísticas puras: prazos, comparação exigência×perfil
  domain/ports/               # Protocols: DocumentParser, DocumentStorage, EmbeddingProvider,
                              #   LLMProvider, repositórios, Clock
  domain/exceptions.py        # exceções de domínio (mapeadas p/ HTTP na presentation)
  application/                # orquestração: importa domain (e langgraph, só em workflows/)
  application/dto/            # DTOs de use case + schemas de extração do LLM (contrato c/ modelo)
  application/use_cases/      # um caso de uso por arquivo
  application/services/       # funções puras: normalização, chunking, validação de citações
  application/workflows/      # LangGraph: state.py, nodes/, graph.py; prompts versionados aqui
  infrastructure/             # adapters concretos dos ports
  infrastructure/database/    # engine/sessão async, models SQLAlchemy, mappers model↔entidade
  infrastructure/repositories/  # um repositório específico por agregado (sem GenericRepository)
  infrastructure/documents/   # pymupdf_parser.py (OCR futuro = novo adapter aqui)
  infrastructure/embeddings/  # voyage.py, fake.py
  infrastructure/llm/         # anthropic.py, fake.py, errors.py (erros tipados, retry, timeout)
  infrastructure/storage/     # local.py (caminho derivado de content_hash)
  presentation/api/           # borda HTTP e ÚNICO lugar de composição:
                              #   routes/ schemas/ dependencies/ exception_handlers/ app.py
  core/                       # config.py (Settings), logging.py (structlog + filtro de segredos)
  main.py
ui/                           # streamlit_app.py + api_client.py (httpx; sem import de licitalens)
migrations/                   # Alembic (env.py deriva URL síncrona do Settings)
scripts/                      # make_fixture_pdf.py, seed.py
tests/                        # unit/ (sem borda real) · integration/ (SQLite em arquivo temporário) · fixtures/
docs/                         # architecture.md, study-guide.md, decisions/ (ADRs), README.md
```

## Como rodar

```bash
uv sync --all-groups                 # instala tudo (dev incluso)
uv run alembic upgrade head          # migrations (cria data/licitalens.db)
uv run fastapi dev src/licitalens/main.py
uv run streamlit run ui/streamlit_app.py
uv run pytest                        # suíte inteira, offline
uv run pytest -m "not integration"   # só units (sem banco)
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

Gate de fase (PLAN §Convenções): pytest + ruff check + ruff format --check +
pyright verdes antes de marcar a fase como concluída.

## Camadas e composição

- Direção de import: `domain ← application ← {infrastructure, presentation}`.
  `core` pode ser importado por infrastructure/presentation; domain e
  application não conhecem `Settings` — recebem valores prontos.
- Composição acontece só em `presentation/api/dependencies/`: é lá que
  Settings escolhe adapter (fake vs real), abre sessão e injeta repositórios
  nos use cases. Use case recebe ports pelo construtor/parâmetro; nunca
  instancia adapter.
- Ports são `typing.Protocol` (estrutural, sem herança); ABC só se precisarmos
  de comportamento compartilhado — hoje não precisamos.
- Fakes (`fake.py` em cada área de infrastructure) são código de produção:
  determinísticos, testados, selecionáveis por env (`LLM_PROVIDER=fake`).
  Fake ≠ mock de teste ad hoc.

## Borda de dados

- Models SQLAlchemy vivem em `infrastructure/database` e **nunca atravessam**
  para application/domain: mappers explícitos convertem model ↔ entidade.
- Sem lazy loading implícito: relacionamentos com `lazy="raise"`; carregamento
  explícito (`selectinload`) onde o use case precisar.
- Transação por use case: quem abre a sessão comita/reverte; repositório não
  comita. Falha no meio do pipeline reverte a escrita parcial.
- Datas timezone-aware UTC (constraint 7 do SPEC); `Decimal` para dinheiro com
  `raw_text` original preservado; PKs `uuid.uuid7()` (ordenáveis por tempo).
- Embeddings: BLOB float32 **normalizado** na escrita; busca por cosseno
  exata no repositório (`math.sumprod` sobre `array('f')` — stdlib, sem
  numpy). Dimensão única via `EMBEDDING_DIMENSION` (1024), validada na
  escrita; trocar exige re-embed (constraint 5). pgvector/HNSW chega com o
  Postgres pós-MVP, atrás do mesmo port.
- SQLite: PRAGMAs `journal_mode=WAL` e `foreign_keys=ON` em toda conexão
  (event listener no engine); o driver devolve datetime naive — o mapper
  grava UTC e reata `timezone.utc` na leitura (constraint 10).

## LLM e evidência

- Toda chamada de modelo passa por `LLMProvider`; toda geração de embedding
  por `EmbeddingProvider`. Nenhum SDK/httpx de IA fora de
  `infrastructure/{llm,embeddings}`.
- Extração usa `messages.parse()` com o schema Pydantic da tarefa; resposta
  que não valida gera um retry único com o erro anexado; persistindo, o
  processamento falha (`FAILED` + `processing_error`) — nunca análise parcial.
- Conteúdo do edital entra no prompt **sempre delimitado como bloco de dados**
  (com aviso de não-confiabilidade), nunca concatenado como instrução.
  Prompts são constantes versionadas em `application/workflows`; mudança de
  prompt é diff revisável.
- Determinístico fica em Python: prazos, somas, ordenações, comparação de
  listas, validação de evidência. O LLM só faz o que exige linguagem.
- Erros tipados no adapter (timeout, rate limit, resposta inválida) com retry
  limitado e backoff; logs registram provedor, modelo, duração e contagens —
  nunca prompt/documento integral nem chaves.

## API

- Schemas de request/response em `presentation/api/schemas`, separados de DTOs
  e entidades — os três variam por motivos diferentes.
- Exceção de domínio → HTTP em `exception_handlers` centrais (envelope de erro
  consistente); rota não faz try/except de negócio.
- `X-Request-ID` gerado/propagado por middleware e presente em todo log da
  requisição.
- Upload valida tipo por magic bytes + limite `MAX_UPLOAD_SIZE_MB` antes de
  persistir qualquer coisa; `original_name` é metadado, nunca caminho.

## Async

- `async` apenas onde há I/O real: rotas, use cases que tocam banco/storage/
  provedores, adapters. Funções puras (normalização, chunking, comparação,
  validação de evidência) são síncronas — não transformar computação em async.
- I/O de arquivo local no adapter de storage é síncrono e curto; se virar
  gargalo, encapsular com `anyio.to_thread` dentro do adapter (não vazar a
  decisão para fora).

## Testes

- `tests/unit`: domain + application com fakes em memória; nenhum banco, rede
  ou filesystem real. É onde vive a maioria dos testes.
- `tests/integration` (marker `integration`): repositórios/migrations/busca
  vetorial contra um SQLite real em arquivo temporário; rotas via
  `TestClient` com fakes de provider.
- Nenhum teste toca rede externa (constraint 6): adapters reais (Anthropic,
  Voyage) são testados com client/transport mockado; execução com chave real é
  verificação manual roteirizada, fora da suíte.
- Fixture central: edital sintético determinístico (gerado por
  `scripts/make_fixture_pdf.py`) com tentativa de injeção embutida — testes de
  segurança afirmam que a instrução não é obedecida e nada vaza.
- Cobertura é instrumento, não meta: mede-se, prioriza-se regra de domínio,
  parsing, chunking, extração, citações, comparação e injection — sem
  perseguir porcentagem.

## Convenções

- Type hints completos; Pyright strict em `src/`. `Any` só com comentário
  justificando na linha. `TYPE_CHECKING` para imports de tipo caros.
- Imports absolutos (`from licitalens.domain...`); um use case por arquivo;
  módulos pequenos — arquivo passando de ~300 linhas é cheiro de mistura de
  responsabilidade.
- Nomes: código e identificadores em inglês (`TenderAnalysis`,
  `submission_deadline`); termos do domínio brasileiro permanecem em pt-BR em
  strings, enums de valor (`pregao_eletronico`) e documentação.
- Enums do domínio para estados e categorias; strings soltas não representam
  estado.
- Erros: exceções de domínio específicas (`DocumentNotFound`,
  `UnparseablePdf`) definidas em `domain/exceptions.py`; adapter converte erro
  de lib externa em erro do domínio/port — exceção de SQLAlchemy/httpx nunca
  cruza a borda de infrastructure.
- Comentários explicam o porquê (constraint, trade-off), não o quê; sem
  decoração. Conhecimento caro (quirk de lib, decisão pesquisada) vai para
  docs/ ou ADR, não para comentário gigante.
- Commits pequenos por tarefa do PLAN, mensagem referenciando o id (ex.:
  `T2.4: use case de upload com dedup por hash`).

## Nunca fazer

- Nunca importar FastAPI, SQLAlchemy, Streamlit ou SDK de provedor em
  `domain/` ou `application/` (única exceção: `langgraph` em
  `application/workflows`, ADR 0003) — a fronteira é o que mantém o núcleo
  testável sem infraestrutura; violação aqui é o refactor mais caro do
  projeto.
- Nunca aceitar ou persistir informação extraída sem `Evidence` validada ou
  `not_found` explícito — regra de ouro; dado sem evidência não tem conserto
  retroativo.
- Nunca interpolar conteúdo do edital (ou pergunta do usuário) como instrução
  de prompt — é dado não confiável (constraint 2); injeção é caso de teste,
  não hipótese.
- Nunca usar o LLM para calcular prazo, somar, ordenar ou comparar listas —
  Python faz isso correto e de graça; o modelo só faz o que exige linguagem.
- Nunca logar chave de API, PDF/página integral, prompt completo ou dados do
  perfil além de ids — logs são o vazamento mais fácil (constraint 8).
- Nunca derivar caminho de storage do nome de arquivo enviado — nome é dado
  não confiável; caminho vem de `content_hash` (path traversal coberto por
  teste em T2.2).
- Nunca criar `GenericRepository`, interface com um único implementador sem
  segundo uso previsto no SPEC, ou camada "para parecer Clean Architecture" —
  abstração vazia é custo sem benefício; os ports existentes cobrem as bordas
  reais.
- Nunca escrever teste que dependa de rede ou chave externa — a suíte é
  offline por contrato (constraint 6); quebra o critério 10 do SPEC.
- Nunca marcar tarefa/fase concluída com pytest, ruff ou pyright falhando —
  gate do PLAN; "quase verde" é vermelho.

## Decisões em aberto

- [x] **psycopg 3 vs asyncpg** — resolvido: psycopg 3, driver único p/ app
      async e Alembic sync (proposta aprovada, 2026-08-04).
- [x] **Onde mora o LangGraph** — resolvido: `application/workflows`, exceção
      deliberada à regra de camadas, registrada em ADR 0003 (2026-08-04).
- [x] **Fake como default de provider** — resolvido: `LLM_PROVIDER=fake` /
      `EMBEDDING_PROVIDER=fake`; projeto executável e testável sem chave
      (2026-08-04).
- [x] **Sem Docker e sem Postgres no MVP** — resolvido: SQLite + aiosqlite,
      busca vetorial exata em memória (stdlib); PostgreSQL+pgvector e Docker
      Compose no pós-MVP do SPEC — a decisão de psycopg acima vale para
      quando o Postgres chegar (revisão do usuário, 2026-08-04).

Nenhuma pendente.
