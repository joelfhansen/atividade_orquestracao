## Estrutura do projeto e função de cada componente

Este projeto cria um ambiente completo para orquestração de pipelines via Airflow, com todos os componentes integrados e prontos para uso. Atualmente permite processamento Spark através do Airflow,e também processamento Python dentro do próprio airflow, utilizando Pandas por exemplo. Veja o que é criado e para que serve cada parte:

- **Airflow**: Orquestrador de pipelines ETL, responsável por agendar, monitorar e executar tarefas. Inclui Webserver, Scheduler, Worker, Triggerer, Dag Processor e API Server.
- **Spark Master**: Gerencia os recursos e distribui os jobs Spark para os Workers.
- **Spark Workers**: Executam os jobs Spark submetidos pelo Master.
- **Spark History Server**: Permite visualizar o histórico de execução dos jobs Spark, usando os arquivos de eventos gerados.
- **Postgres**: Banco de dados usado pelo Airflow para persistência de metadados e estado das tarefas.
- **Redis**: Broker de mensagens para o CeleryExecutor do Airflow, gerenciando filas de tarefas distribuídas.
- **Flower**: Interface web para monitoramento dos workers Celery do Airflow.
- **Environment Configurator**: Serviço responsável por criar as pastas compartilhadas, ajustar permissões e gerar as chaves SSH usadas na comunicação segura entre Airflow e Spark.
- **Volumes compartilhados**:
  - `logs/airflow`: Armazena logs de execução do Airflow.
  - `logs/spark-events`: Armazena arquivos de eventos dos jobs Spark, usados pelo History Server.
  - `ssh`: Guarda as chaves SSH para autenticação entre Airflow e Spark Master.
  - `dags`, `plugins`, `config`, `app`, `data`: Pastas para DAGs, plugins, configurações, scripts e dados usados nos pipelines.

Todos esses componentes são integrados via Docker Compose, com dependências e healthchecks para garantir que o ambiente esteja sempre pronto para uso.

## Instruções para configurar e iniciar o ambiente Airflow + Spark

### 1. Pré-requisitos
- Docker e Docker Compose instalados
- Linux recomendado (testado no Ubuntu 24.04)

### 2. Clonando o projeto
```bash
git clone <repo-url>
cd atividade_orquestracao
```

### 3. Configurando variáveis de ambiente

Você pode criar um arquivo `.env` na raiz do projeto para definir os UIDs dos serviços:
```
AIRFLOW_UID=50000
SPARK_UID=185
```
Essas variáveis não são obrigatórias. Se não configurar o `.env`, os valores padrão serão usados:
- `AIRFLOW_UID=50000` para o Airflow
- `SPARK_UID=185` para o Spark
Se quiser usar outros UIDs, ajuste conforme seu usuário local.


### 4. Build das imagens customizadas
Opcional: Caso queira garantir que as imagens estejam atualizadas antes de subir o ambiente, rode:
```bash
docker compose build
```
Se preferir, pode pular este passo e usar o comando do próximo item, que já inclui a opção `--build`.

### 5. Inicializando o ambiente

```bash
docker compose up -d --build
```
Após este comando, o ambiente é preparado automaticamente. Veja o que acontece sem intervenção manual:

#### O que acontece automaticamente:
- **Criação e ajuste de permissões das pastas compartilhadas:**
  O serviço `environment-configurator` garante que as pastas `logs/airflow`, `logs/spark-events` e `ssh` existam e estejam com as permissões corretas para Airflow e Spark. Não é necessário rodar comandos de permissão manualmente, exceto em casos de erro.
- **Geração de chaves SSH:**
  O `environment-configurator` gera automaticamente o par de chaves SSH (`id_rsa` e `id_rsa.pub`) na pasta `ssh/`, com permissões seguras. Essas chaves são usadas para autenticação entre Airflow e Spark Master via SSHOperator.
- **Instalação do cliente SSH:**
  O container spark-master instala o `openssh-client` para permitir geração das chaves e testes de conexão.
- **Configuração das conexões do Airflow:**
  O script `airflow_init_connections.sh` é executado pelo serviço `airflow-init`, criando as conexões `spark_default` e `spark_master_ssh` no Airflow automaticamente.
- **Build das imagens customizadas:**
  As imagens do Airflow e Spark Master são construídas conforme os Dockerfiles do projeto, já com dependências e configurações necessárias.
- **Inicialização dos serviços em ordem correta:**
  Todos os serviços Airflow e Spark dependem do `environment-configurator` estar saudável, garantindo que permissões e chaves estejam prontas antes do start. Postgres e Redis também são inicializados e verificados via healthcheck antes do Airflow iniciar.
- **Compartilhamento de volumes:**
  As pastas compartilhadas (`logs`, `ssh`, `app`, etc.) são montadas nos containers conforme necessário, permitindo acesso aos dados, logs e scripts entre Airflow e Spark.
- **Configuração do Airflow:**
  O Airflow é inicializado com as configurações do arquivo `config/airflow.cfg` e variáveis de ambiente definidas no compose. Usuário e senha padrão do Airflow são criados automaticamente (por padrão, para ambiente de teste: `airflow:airflow`).
- **Configuração do Spark:**
  Spark Master, Workers e History Server são configurados para usar o diretório de eventos compartilhado (`logs/spark-events`), permitindo visualização dos jobs submetidos.
- **Healthchecks e dependências:**
  Todos os serviços críticos possuem healthchecks para garantir que só iniciam quando dependências estão prontas.

---
O ambiente estará pronto para uso, com permissões, chaves SSH, conexões do Airflow e serviços já configurados. Permissões e configurações são automáticas. Só faça ajustes manuais se houver erro de permissão ou acesso.

### 6. Acessando os serviços
- Airflow Webserver: http://localhost:9080
- Spark Master: http://localhost:8080
- Spark History Server: http://localhost:18080

### 7. Submetendo jobs Spark via Airflow
Para orquestrar jobs Spark via Airflow, utilize as conexões criadas automaticamente:
- Use a conexão **`spark_master_ssh`** para submeter jobs via **SSHOperator** (execução remota de comandos no Spark Master).
- Use a conexão **`spark_default`** para submeter jobs via **SparkSubmitOperator** (submissão direta de jobs Spark).

### 8. Logs e eventos
- Logs do Airflow: `logs/airflow/`
- Eventos do Spark: `logs/spark-events/` (usados pelo History Server)

### 9. Dicas de troubleshooting
- Consulte os logs dos containers com `docker compose logs <serviço>` para identificar os pontos de falha.

---
Ambiente pronto para desenvolvimento e orquestração de pipelines Airflow + Spark!
