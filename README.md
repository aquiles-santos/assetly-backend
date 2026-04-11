# Assetly Backend

API backend do Assetly construída com Flask e SQLite para cadastro, consulta, sincronização e importação de ativos de mercado.

## Requisitos

- Docker e Docker Compose para o fluxo recomendado de execução
- Python 3.8 ou superior e `make` apenas para o fluxo local alternativo

## Escolha recomendada

Use Docker como caminho oficial de execução.

O fluxo com virtualenv está disponível, mas deve ser tratado como alternativa para desenvolvimento local, principalmente em Linux e macOS.

## Quick Start

Para a maioria dos usuários, o setup é este:

```bash
docker compose up --build
```

Depois acesse:

```text
http://127.0.0.1:5000
```

Swagger:

```text
http://127.0.0.1:5000/apidocs
```

## Execução recomendada com Docker

O caminho mais previsível para rodar o projeto em Linux, macOS e Windows é usar Docker.

Suba a API com:

```bash
docker compose up --build
```

Esse fluxo:

- instala as dependências dentro do container
- cria o schema do banco automaticamente ao iniciar
- carrega a base inicial de ativos automaticamente na primeira execução
- persiste o SQLite em um volume Docker

Para parar os containers:

```bash
docker compose down
```

Para remover também o banco persistido e recriar tudo do zero:

```bash
docker compose down -v
docker compose up --build
```

Se você quiser subir sem a carga inicial automática:

```bash
AUTO_SEED_DB=0 docker compose up --build
```

## Fluxo local alternativo

Use este fluxo apenas se você quiser rodar o projeto sem Docker.

1. Acesse a pasta do projeto.

2. Crie o ambiente virtual e instale as dependências.

```bash
make init
```

3. Inicialize o banco de dados.

```bash
make init-db
```

4. Opcionalmente, carregue a base inicial de ativos.

```bash
make seed-db
```

### Script automatizado para Windows (sem Docker)

Se você estiver no Windows e quiser evitar Docker e `make`, use o script PowerShell abaixo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-local-win.ps1
```

Se estiver usando `cmd.exe`, o comando é o mesmo:

```bat
powershell -ExecutionPolicy Bypass -File .\scripts\run-local-win.ps1
```

Esse script executa automaticamente:

- upgrade de `pip`, `setuptools` e `wheel`
- instalação de dependências via `requirements.txt`
- inicialização do banco SQLite
- carga inicial de ativos (seed)
- start da API em `http://127.0.0.1:5000`

Parâmetros úteis:

- sem seed inicial:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-local-win.ps1 -SkipSeed
```

- somente setup (não sobe a API):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-local-win.ps1 -NoRun
```

- escolher manualmente o comando Python (ex.: apenas `python`):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-local-win.ps1 -PythonCommand "python"
```

### Passo a passo para Windows (sem Docker e sem make)

Se o script não funcionar no seu ambiente, siga este fluxo manual.

1. Instale o Python 3.10+ (recomendado via `winget`):

```bat
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
```

2. Feche e reabra o terminal.

3. Desative aliases da Microsoft Store para evitar conflito com `python`:

- abra: `Configurações (Settings) > Aplicativos (Apps) > Configurações avançadas de aplicativos (Advanced app settings) > Aliases de execução de aplicativos (App execution aliases)`
- desative: `python.exe` e `python3.exe`

Observação: em algumas instalações do Windows essas opções podem não aparecer. Se você não encontrar esses aliases e os comandos `where python` e `python --version` funcionarem corretamente, pode seguir para o passo 4 sem problema.

4. Valide a instalação:

```bat
where python
python --version
```

O caminho não deve apontar apenas para `WindowsApps`.

5. Na pasta do projeto, instale dependências:

```bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

6. Inicialize o banco:

```bat
python -c "from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app)"
```

7. (Opcional) Faça seed da base inicial:

```bat
python -c "from app import create_app; from app.utils.db_init import seed_db; app=create_app(); seed_db(app)"
```

8. Inicie a API:

```bat
python run.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

Swagger:

```text
http://127.0.0.1:5000/apidocs
```

## Configuração do ambiente local

O projeto usa uma virtualenv em `.venv` e um banco SQLite local. Esse fluxo continua disponível como alternativa para desenvolvimento local, principalmente em Linux e macOS. Em Linux, o alvo `make init` tenta usar `python3` automaticamente e aceita override via `BOOTSTRAP_PYTHON=/caminho/do/python3`.

Observação para Debian/Ubuntu: se `make init` falhar informando que `ensurepip` não está disponível, instale o suporte a virtualenv do sistema com:

```bash
sudo apt install python3-venv
```

Se preferir, o próprio fluxo local pode tentar instalar essa dependência automaticamente:

```bash
make init AUTO_INSTALL_SYSTEM_DEPS=1
```

Em terminais interativos no Debian/Ubuntu, `make init` também pode pedir sua confirmação antes de executar a instalação via `sudo apt-get install -y python3-venv`.

Comandos disponíveis:

- `make init`: cria a virtualenv e instala as dependências
- `make init-db`: cria o schema do banco
- `make seed-db`: importa a base inicial a partir do CSV versionado em `data/seed_assets.csv`
- `make reset-db`: recria o banco do zero sem carga inicial
- `make test`: executa os testes automatizados
- `make setup`: executa instalação e inicialização básica do projeto

## Como executar

Para iniciar a API localmente:

```bash
make run
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:5000
```

Para expor a aplicação com Gunicorn:

```bash
make serve
```

## Documentação da API

Para subir a aplicação com acesso à documentação Swagger:

```bash
make docs
```

Depois acesse:

```text
http://127.0.0.1:5000/apidocs
```

## Importação de ativos por CSV

O importador aceita arquivos CSV com uma coluna contendo o símbolo do ativo. Os cabeçalhos aceitos incluem:

- `symbol`
- `ticker`
- `code`
- `asset`

Colunas opcionais podem sobrescrever dados retornados pelo Yahoo Finance:

- `name`
- `asset_type`
- `sector`
- `exchange`
- `currency`
- `notes`

Exemplo de arquivo:

```csv
symbol,asset_type,notes
AAPL,equity,Importado da watchlist NASDAQ
MSFT,equity,Importado da watchlist NASDAQ
PETR4.SA,equity,Importado da watchlist B3
VALE3.SA,equity,Importado da watchlist B3
```

Para importar:

```bash
make import-csv CSV=./assets.csv
```

Para atualizar ativos já existentes:

```bash
make import-csv CSV=./assets.csv UPDATE=1
```

## CORS para o frontend

Por padrão, a API aceita as seguintes origens:

- `null`, para abertura direta do frontend via `file://`
- `http://localhost:5500`
- `http://127.0.0.1:5500`

Para sobrescrever a lista de origens permitidas, defina a variável abaixo:

```bash
export CORS_ALLOWED_ORIGINS="null,http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000"
```

## Estrutura principal

- `app/`: código principal da API
- `app/integrations/`: integrações externas, como Yahoo Finance
- `app/models/`: modelos persistidos
- `app/utils/`: utilitários de banco e importação
- `data/`: arquivos de carga inicial
- `tests/`: testes automatizados
