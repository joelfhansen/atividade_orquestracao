# Atividade Prática: Orquestração de Pipelines com Dados JSON

Resultado da atividade: [Consulte as instruções detalhadas de configuração e execução](INSTRUCTIONS.md).

## Objetivo

O objetivo desta atividade é praticar o uso de uma ferramenta de orquestração (como Apache Airflow, Prefect, Mage ou outras) para construir um pipeline simples com três etapas principais:

1. **Ingestão** dos dados a partir de dois arquivos JSON;
2. **Transformação** dos dados em uma única estrutura consolidada;
3. **Geração** de uma tabela final cruzando as informações dos dois arquivos.

---

## Estrutura de Dados

O repositório contém os seguintes arquivos de entrada, localizados na pasta `data/raw/`:

- `listing_scrape.json`.
- `listing_availability_scrape.json`.

---

## Etapas do Pipeline

### 1. Ingestão
- Carregar os dois arquivos JSON brutos a partir do diretório `data/raw/`.

### 2. Transformação
- Realizar um **join** (cruzamento) entre os dois conjuntos de dados.


### 3. Geração da Tabela Final
- Salvar os dados transformados em um novo arquivo no diretório `data/processed/` com o nome `final_table.parquet`.

---

## 🧪 Requisitos da Atividade

- Use uma ferramenta de orquestração de sua escolha para controlar as etapas do pipeline;
- O pipeline deve ser reexecutável (idempotente);
- Utilize boas práticas de modularização e logging;
- O pipeline deve prever possíveis falhas (ex: arquivos ausentes, campos nulos, schemas incompatíveis);
- Ao final, o pipeline deve gerar logs indicando o sucesso ou falha de cada etapa.

---

## Sugestão de Ferramentas

- [Apache Airflow](https://airflow.apache.org/)
- [Prefect](https://www.prefect.io/)
- [Mage](https://www.mage.ai/)
- [Dagster](https://dagster.io/)
- Ou scripts Python com agendamento via cron como alternativa simplificada

---

## Estrutura Esperada do Projeto

   ```bash
atividade_orquestracao/
├── dags/ # Código do pipeline (caso use Airflow)
├── flows/ # Código do pipeline (caso use Prefect, Mage, etc.)
├── data/
│ ├── raw/
│ │ ├── listing_scrape.json
│ │ └── listing_availability_scrape.json
│ └── processed/
│ │ ├── final_table.parquet
├── requirements.txt
└── README.md
   ```

## Entrega Esperada

- Um repositório com o pipeline funcionando e instruções de execução no `README.md`;
- O script ou DAG deve ser facilmente executável;
- Inclua prints ou outputs mostrando o sucesso da execução e o arquivo final gerado.


## Como Começar: Fork e Configuração Local

1. **Fork este repositório** para sua conta GitHub:
   - Clique no botão **Fork** no canto superior direito da página.
   - Escolha sua conta pessoal ou organizacional como destino.

2. **Clone o repositório forkado** para sua máquina local:

   ```bash
   git clone https://github.com/<usuario>/atividade_orquestracao.git
   ```

