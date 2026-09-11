# Cofre de Artefatos de Pesquisa Científica

## Tema e Objetivo
Este projeto foi desenvolvido como o Trabalho Prático 1 da disciplina **Desenvolvimento de Software para Persistência** da Universidade Federal do Ceará (Campus Quixadá). 

O sistema consiste em uma API construída com **FastAPI** que atua como um **Cofre Digital**, cujo domínio específico (Tema 9) é o gerenciamento de artefatos de pesquisa científica. A aplicação gerencia o ciclo de vida (armazenamento, metadados, integridade, segurança e backup) de materiais acadêmicos como artigos, datasets, formulários, relatórios, imagens, scripts e resultados experimentais.

## Requisitos do Sistema
* Python 3.10 ou superior
* Gerenciador de pacotes e ambientes `uv`

## Bibliotecas Utilizadas
* **FastAPI**: Framework web para construção da API.
* **Uvicorn**: Servidor ASGI para execução do projeto.
* **Pydantic & Pydantic-Settings**: Validação de dados, tipagem de metadados e leitura de configurações.
* **PyYAML**: Empregado para manipulação e leitura do arquivo externo de configuração.
* **Aiofiles**: Manipulação assíncrona de arquivos no sistema de armazenamento.

## Instruções de Instalação e Execução

### 1. Clonar o repositório
```bash
git clone <url-do-seu-repositorio>
cd science_vault
```

### 2. Criar o ambiente virtual e instalar as dependências com o uv
O projeto utiliza o `uv` para gerenciamento rápido de ambiente e pacotes.

```bash
# Cria o ambiente virtual (.venv) e sincroniza o projeto
uv venv
uv sync
```

### 3. Ativar o ambiente virtual
```bash
# No Linux/macOS:
source .venv/bin/activate
# No Windows (Command Prompt):
.venv\Scripts\activate
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

### 4. Executar a aplicação
```bash
uvicorn main:app --reload
```
A API estará disponível em `http://127.0.0.1:8000`. A documentação interativa Swagger poderá ser acessada em `http://127.0.0`.

## Estrutura do Projeto (Monólito Modular)
A arquitetura do sistema segue o padrão de monólito modular, separando a infraestrutura global das regras e operações de negócio.

```text
src/
│
├── config/                  # Configurações globais
│   ├── __init__.py
│   └── settings.py          # Leitura dinâmica do config.yaml
│
├── core/                    # Infraestrutura compartilhada
│   ├── __init__.py
│   ├── logging_config.py    # Configuração nativa de logs
│   └── security.py          # Funções de hashing (SHA-256)
│
├── modules/                 # Módulos de Negócio
│   ├── vault/               # Módulo Principal do Cofre
│   │   ├── __init__.py
│   │   ├── models.py        # Modelos de metadados gerais e da pesquisa
│   │   ├── routes.py        # Endpoints do cofre
│   │   └── service.py       # Persistência em JSON e arquivos físicos
│   │
│   └── operations/          # Módulo de Suporte e Utilitários
│       ├── __init__.py
│       ├── routes.py        # Endpoints de backup, exportação e estatísticas
│       └── service.py       # Lógica de zip, CSV e agregadores
│
├── storage/                 # Diretórios locais de dados (gerados automaticamente)
│   ├── documents/           # Arquivos científicos físicos
│   ├── metadata/            # Arquivo documents.json
│   ├── backups/             # Backups em formato ZIP
│   └── logs/                # Arquivo system.log
│
├── config.yaml              # Configurações externas configuráveis
├── main.py                  # Ponto de entrada do FastAPI
└── README.md                # Documentação do sistema
```

## Metadados do Domínio (Pesquisa Científica)
Cada artefato armazenado no sistema possui metadados estruturados via Pydantic. Além dos campos gerais obrigatórios, foram implementados os seguintes campos específicos para o domínio científico:

* **project**: Nome do projeto de pesquisa ao qual o artefato pertence.
* **researcher**: Nome do pesquisador responsável pelo upload ou pela autoria do artefato.
* **artifact_type**: Classificação do arquivo no contexto científico (ex: Article, Dataset, Script, Report).
* **research_stage**: Fase atual da pesquisa em que o arquivo se aplica (ex: Data Collection, Analysis, Writing, Review).
* **reference_date**: Data de referência ou geração do artefato científico.

### Exemplo de Estrutura do JSON de Metadados:
```json
{
  "id": 1,
  "original_name": "experiment_phase1.csv",
  "stored_name": "1_experiment_phase1.csv",
  "extension": ".csv",
  "mime_type": "text/csv",
  "size": 102450,
  "category": "data",
  "description": "Dataset contendo as medições da primeira etapa do acelerador",
  "upload_date": "2026-09-11T20:25:00",
  "sha256": "8f43c0a4e...",
  "project": "Project Alpha - Particle Physics",
  "researcher": "Dr. Carlos Eduardo",
  "artifact_type": "Dataset",
  "research_stage": "Data Collection",
  "reference_date": "2026-09-11"
}
```

## Principais Endpoints da API

### Módulo Vault (`/documents`)
* `POST /documents`: Realiza o upload de um arquivo físico e envia seus metadados associados.
* `GET /documents`: Lista todos os artefatos científicos cadastrados no cofre.
* `GET /documents/{id}`: Recupera detalhadamente os metadados de um artefato específico.
* `GET /documents/{id}/download`: Faz o download do arquivo binário ou textual original.
* `PUT /documents/{id}`: Atualiza os metadados permitidos do artefato (como descrição, etapa da pesquisa e pesquisador).
* `DELETE /documents/{id}`: Remove o registro do catálogo JSON e deleta o arquivo físico do armazenamento.
* `GET /documents?project=name&researcher=name`: Filtra o catálogo por parâmetros específicos do domínio ou gerais.
* `GET /documents/{id}/integrity`: Compara o hash SHA-256 atual do arquivo físico com o valor registrado no upload para verificar adulterações.

### Módulo Operations (`/operations`)
* `GET /operations/stats`: Exibe métricas consolidadas (espaço total em bytes, quantidade por extensão, por categoria e distribuição de artefatos por projeto de pesquisa).
* `GET /operations/integrity-check`: Realiza uma varredura global no sistema informando arquivos íntegros, alterados e registros órfãos sem arquivo físico correspondente.
* `GET /operations/export/csv`: Gera e exporta um arquivo CSV contendo todo o catálogo de metadados de pesquisa cadastrados.
* `POST /operations/backup`: Cria um arquivo ZIP compactado contendo todos os documentos e metadados gerais atuais do sistema.
* `GET /operations/backups`: Lista todos os arquivos de backup gerados disponíveis na pasta de armazenamento.

## Funcionalidade Específica do Tema (F16)
Conforme a restrição obrigatória do Tema 9, foi implementado o endpoint de **Backup Seletivo por Projeto de Pesquisa**.

* **Endpoint**: `POST /operations/backup/project`
* **Funcionamento**: O endpoint aceita um parâmetro de consulta contendo o nome do projeto de pesquisa (`project`). O sistema filtra internamente no arquivo de metadados `documents.json` todos os registros vinculados àquele projeto exato, localiza seus respectivos arquivos físicos em `storage/documents/` e gera de maneira isolada um arquivo compactado `.zip` contendo exclusivamente os artefatos daquela pesquisa específica. O arquivo gerado é persistido no diretório de backups configurado e listado nas auditorias.
