# Assetly Backend

API backend do Assetly construída com Flask e SQLite para cadastro, consulta, sincronização e importação de ativos de mercado.

## Requisitos

- Python 3.8 ou superior
- `make` instalado no ambiente

## Instalação

Siga os passos abaixo para configurar o ambiente local:

1. Acesse a pasta do backend.
2. Crie o ambiente virtual e instale as dependências.
3. Inicialize o banco de dados.
4. Opcionalmente, carregue a base inicial de ativos.

Comandos:

```bash
make init
make init-db
make seed-db
```

## Configuração do ambiente local

O projeto usa uma virtualenv em `.venv` e um banco SQLite local.

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
