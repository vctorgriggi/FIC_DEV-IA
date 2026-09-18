# Aula Dia 17 — ETL no Apache Hop com 3 fontes de dados

ETL construído no Apache Hop 2.19 que baixa **três fontes públicas direto pelas APIs**, cruza os
dados por município e publica um CSV com indicadores que só existem quando as três se encontram.

Recorte: **as 27 capitais brasileiras** (é o nível em que o INMET publica condição meteorológica
consolidada por município).

## 1) As três fontes

| # | Fonte | Endpoint | O que traz |
|---|-------|----------|-----------|
| 1 | INMET | `${INMET_BASE_URL}/condicao/capitais/${PRM_DATA_REF}` | temperatura mín./máx., umidade mínima e chuva máxima do dia |
| 2 | IBGE  | `${IBGE_BASE_URL}/agregados/6579/periodos/2024/variaveis/9324?localidades=N6[all]` | população residente estimada 2024 (5.571 municípios) |
| 3 | IBGE  | `${IBGE_BASE_URL}/agregados/1301/periodos/2010/variaveis/615?localidades=N6[all]` | área territorial em km² (5.565 municípios) |

O download é feito **dentro do Hop**, pelo transform `REST client` — não há `curl`, script Python
nem arquivo baixado à mão em nenhum ponto do fluxo.

### Chave de integração

As duas fontes do IBGE já trazem o **código IBGE do município**, então o cruzamento entre elas é
direto. O INMET identifica a estação apenas pelo nome da capital, em caixa alta e sem padrão de
acentuação (`SAO PAULO`, mas `MACEIÓ`). Por isso existe a tabela de conformidade
`dados/entrada/capitais_ibge.csv` (27 linhas: nome INMET → código IBGE → município → UF), que é o
que amarra a fonte meteorológica às duas fontes do IBGE.

## 2) Estrutura do projeto

```
dia17/
├── project-config.json                     # projeto Hop (gerado pelo hop-conf)
├── config/
│   ├── env-dev.json                        # ambiente de desenvolvimento (variáveis)
│   └── env-prod.json                       # mesmo ETL apontando para outros diretórios
├── pipelines/
│   ├── extrai_inmet_clima.hpl              # fonte 1  → staging
│   ├── extrai_ibge_populacao.hpl           # fonte 2  → staging
│   ├── extrai_ibge_area.hpl                # fonte 3  → staging
│   └── integra_clima_populacao_area.hpl    # junta as 3 e calcula os indicadores
├── workflows/
│   └── main_dia17.hwf                      # orquestra os 4 pipelines na ordem
└── dados/
    ├── entrada/capitais_ibge.csv           # de-para capitais INMET ↔ código IBGE
    ├── staging/                            # camada bronze (1 CSV por fonte)
    └── saida/capitais_clima_populacao_area.csv
```

Fluxo de cada extração:
`Generate rows → Get variables → REST client → JSON Input → Text file output (staging)`

Fluxo da integração:
`de-para capitais → Stream lookup (população) → Stream lookup (área) → Stream lookup (clima) → Select values (cast) → Calculator → Sort rows → Text file output`

## 3) Parametrização

Nenhuma URL, caminho ou período está escrito dentro de um transform. Tudo vem de variáveis do
**environment** (`config/env-*.json`), e os pipelines ainda expõem parâmetros próprios:

| Variável | Valor em dev | Para que serve |
|----------|--------------|----------------|
| `INMET_BASE_URL` | `https://apitempo.inmet.gov.br` | troca de host da API do INMET |
| `IBGE_BASE_URL` | `https://servicodados.ibge.gov.br/api/v3` | troca de host da API do IBGE |
| `HTTP_USER_AGENT` | `Mozilla/5.0 (compatible; ApacheHop/2.19; FIC-DEV-IA)` | o INMET recusa a conexão sem `User-Agent` |
| `DATA_REF` | `2026-09-16` | data consultada no INMET |
| `IBGE_AGREGADO_POP` / `IBGE_VARIAVEL_POP` / `IBGE_PERIODO_POP` | `6579` / `9324` / `2024` | qual pesquisa e qual ano de população |
| `IBGE_AGREGADO_AREA` / `IBGE_VARIAVEL_AREA` / `IBGE_PERIODO_AREA` | `1301` / `615` / `2010` | qual pesquisa e qual ano de área |
| `IBGE_NIVEL` | `N6[all]` | nível geográfico (N6 = municípios) |
| `DIR_ENTRADA` / `DIR_STAGING` / `DIR_SAIDA` | `${PROJECT_HOME}/dados/...` | diretórios do ETL |

Parâmetros de pipeline (têm default vindo da variável, e podem ser sobrescritos na execução):
`PRM_DATA_REF` (INMET) e `PRM_AGREGADO` / `PRM_VARIAVEL` / `PRM_PERIODO` (IBGE).

**Migrar de ambiente = trocar o environment**, sem tocar em um único `.hpl`:

```bash
hop-run.sh -j dia17 -e dia17-prod -r local -f '${PROJECT_HOME}/workflows/main_dia17.hwf'
```

E rodar outra data sem editar nada:

```bash
hop-run.sh -j dia17 -e dia17-dev -r local \
  -f '${PROJECT_HOME}/workflows/main_dia17.hwf' -p PRM_DATA_REF=2026-09-14
```

## 4) Como executar

Registrar o projeto e o ambiente (uma vez):

```bash
cd ~/Downloads/hop
./hop-conf.sh -pc -p dia17 -ph <caminho>/Engenharia-Dados/Dia-17/dia17
./hop-conf.sh -ec -e dia17-dev  -ep dia17 -eu Development \
  -eg <caminho>/Engenharia-Dados/Dia-17/dia17/config/env-dev.json
./hop-conf.sh -ec -e dia17-prod -ep dia17 -eu Production \
  -eg <caminho>/Engenharia-Dados/Dia-17/dia17/config/env-prod.json
```

Rodar tudo:

```bash
./hop-run.sh -j dia17 -e dia17-dev -r local -f '${PROJECT_HOME}/workflows/main_dia17.hwf'
```

Ou abrir na interface: `./hop-gui.sh`, selecionar o projeto **dia17** e executar
`workflows/main_dia17.hwf`.

## 5) Resultado

`dados/saida/capitais_clima_populacao_area.csv` — 27 linhas, ordenadas por densidade:

| Coluna | Origem |
|--------|--------|
| `codigo_ibge`, `municipio`, `uf` | de-para de capitais |
| `data_referencia` | INMET |
| `populacao` | IBGE 6579 |
| `area_km2` | IBGE 1301 |
| `densidade_hab_km2` | **calculado**: população ÷ área (fontes 2 + 3) |
| `temp_minima_c`, `temp_maxima_c`, `umidade_minima_pct`, `chuva_maxima_mm` | INMET |
| `amplitude_termica_c` | **calculado**: máxima − mínima (fonte 1) |

### Leituras da execução de 2026-09-16

- **Fortaleza (CE)** é a capital mais adensada: 8.175 hab/km². **Porto Velho (RO)**, a mais
  espraiada: 15 hab/km² — uma diferença de 540×, com populações da mesma ordem de grandeza
  (2,57 mi × 0,51 mi). O que separa as duas é a área: 315 km² contra 34.096 km².
- Somadas, as 27 capitais concentram **49,2 milhões de pessoas em 96,9 mil km²** (507 hab/km²),
  menos de 1,2% do território nacional.
- Cruzando com o clima: as capitais mais densas (≥ 2.000 hab/km², todas litorâneas) tiveram
  **amplitude térmica média de 8,8 °C**, contra **12,2 °C** nas capitais menos densas — que são
  as do interior e da Amazônia. Densidade alta no Brasil é, na prática, sinônimo de capital
  litorânea, e o mar amortece a variação de temperatura.
- Extremos do dia: **Teresina (PI)** com 40,0 °C e a maior amplitude (17,3 °C);
  **Porto Alegre (RS)** com a mínima mais baixa (9,2 °C); **Natal (RN)** com a menor
  amplitude (5,7 °C).

## 6) Detalhes de implementação que valem nota

- **`User-Agent` obrigatório**: a API do INMET encerra a conexão sem esse header. Ele entra no
  fluxo pelo `Get variables` e é mapeado como header no `REST client`.
- **Asterisco do INMET**: valores provisórios vêm como `24.3*` e ausentes como `*`. O transform
  `Replace in string` remove o asterisco e o `Select values` converte para número — string vazia
  vira nulo. Em 2026-09-16, 6 das 27 capitais estavam sem leitura.
- **`...` do IBGE**: um município publica população como `...`. Os números do IBGE são lidos como
  texto no staging e só convertidos **depois** do lookup, sobre as 27 linhas que interessam —
  assim um valor inválido em qualquer um dos 5.571 municípios não derruba o ETL.
- **Cuidado com o `Calculator`**: o tipo do resultado segue o campo A. Com `populacao` como
  Integer, `populacao ÷ area_km2` virava divisão inteira (Belo Horizonte saía com 7.300 em vez de
  7.291,31). A população é convertida para Number antes do cálculo, e a máscara `#` na saída
  garante que o CSV continue sem casas decimais.
- **Sem sorts desnecessários**: a junção usa `Stream lookup` (tabela em memória) em vez de
  `Merge join`, que exigiria ordenar os 5.571 municípios três vezes.
