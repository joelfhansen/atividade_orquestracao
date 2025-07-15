## Estrutura do projeto e função de cada componente

Este projeto implementa uma plataforma de orquestração de pipelines ETL com Apache Airflow e Apache Spark, totalmente automatizada via Docker Compose. O ambiente permite:

- Orquestração de pipelines Spark e Pandas via Airflow, com equivalência funcional e comparação direta dos resultados.
- Submissão de jobs Spark por SSHOperator (execução remota) e SparkSubmitOperator (submissão direta).
- Sanitização robusta de arquivos JSON para garantir ingestão confiável, mesmo com dados malformados.
- Automação de permissões, geração de chaves SSH, configuração de conexões e inicialização dos serviços.
- Logs centralizados e histórico de jobs Spark acessível via Spark History Server.

**Componentes principais:**
- **Airflow**: Orquestrador de pipelines ETL, agendamento, monitoramento e execução de tarefas. Inclui Webserver, Scheduler, Worker, Triggerer, Dag Processor e API Server.
- **Spark Master**: Gerencia recursos e distribui jobs Spark para os Workers.
- **Spark Workers**: Executam jobs Spark submetidos pelo Master.
- **Spark History Server**: Visualização do histórico de jobs Spark, usando arquivos de eventos.
- **Postgres**: Banco de dados do Airflow.
- **Redis**: Broker de mensagens para o CeleryExecutor do Airflow.
- **Flower**: Interface web para monitoramento dos workers Celery.
- **Environment Configurator**: Criação de pastas compartilhadas, permissões e geração de chaves SSH para comunicação segura entre Airflow e Spark.
- **Volumes compartilhados**:
  - `logs/airflow`: Logs do Airflow.
  - `logs/spark-events`: Eventos dos jobs Spark.
  - `ssh`: Chaves SSH para autenticação Airflow/Spark.
  - `dags`, `plugins`, `config`, `app`, `data`: DAGs, plugins, configs, scripts e dados dos pipelines.

Todos os componentes são integrados via Docker Compose, com dependências, healthchecks e automação de setup.

## Instruções para configurar e iniciar o ambiente Airflow + Spark

### 1. Pré-requisitos
- Docker e Docker Compose instalados
- Linux recomendado (testado no Ubuntu 24.04)

### 2. Clonando o projeto
```bash
git clone <repo-url>
cd atividade_orquestracao
```

### 4. Dependências Python customizadas

O projeto utiliza dependências Python adicionais para garantir robustez no processamento de dados, especialmente para leitura de arquivos JSON potencialmente malformados. Certifique-se de que os arquivos `requirements-airflow.txt` e `requirements-spark.txt` (Spark) incluem:

```
json5
```

O pacote `json5` é fundamental para leitura tolerante de arquivos JSON exportados de sistemas externos, evitando erros de parsing em pipelines Spark e Airflow.

### 5. Build das imagens customizadas
**Recomendado:** Sempre rode o build das imagens customizadas antes de subir o ambiente, especialmente após alterações em dependências ou Dockerfiles:
```bash
docker compose build
```
Esse comando garante que todas as dependências (incluindo `json5`) estejam presentes nos containers Airflow e Spark.

### 5. Inicializando o ambiente

```bash
docker compose up -d --build
```
Após este comando, o ambiente é preparado automaticamente. Veja o que acontece sem intervenção manual:

#### O que acontece automaticamente:
- **Criação e ajuste de permissões das pastas compartilhadas:**
  O serviço `environment-configurator` garante que as pastas `logs/airflow`, `logs/spark-events` e `ssh` existam e estejam com as permissões corretas para Airflow e Spark. Não é necessário rodar comandos de permissão manualmente, exceto em casos de erro.
- **Geração de chaves SSH:**
  O `environment-configurator` gera automaticamente o par de chaves SSH (`id_rsa` e `id_rsa.pub`) na pasta `ssh/`, com permissões seguras. Essas chaves são usadas para autenticação entre Airflow e Spark Master via SSHOperator. O container instala o `openssh-client` para permitir geração das chaves e testes de conexão.
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
