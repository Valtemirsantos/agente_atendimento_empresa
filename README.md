# Agente de Atendimento da Empresa

API em Python para atendimento ao cliente, desenvolvida com FastAPI e Agno, com suporte a integração com OpenAI para respostas inteligentes e encaminhamento seguro para atendimento humano quando necessário.

## Visão geral

Este projeto oferece:

- atendimento automatizado para clientes via chat;
- consulta local de produtos e pedidos;
- sanitização de dados sensíveis antes de enviar conteúdo ao modelo;
- rate limiting e validação de origem por chave de acesso;
- suporte a retenção limitada de identificadores de sessão;
- possibilidade de backup criptografado do banco local.

## Requisitos

- Python 3.12+
- Ambiente virtual local
- Chave da OpenAI para uso do modelo de IA

## Configuração rápida

No PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Depois, preencha as variáveis no arquivo `.env` com valores reais para seu ambiente local. Não versionar esse arquivo.

## Variáveis de ambiente

O arquivo `.env.example` contém o modelo mínimo necessário:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///empresa.db
INTERNAL_API_KEY=
ACCESS_KEYS={"support":"replace_support_key","admin":"replace_admin_key"}
CONVERSATION_HASH_KEY=
CONVERSATION_RETENTION_DAYS=30
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW_SECONDS=60
REQUIRE_HTTPS=false
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
BACKUP_ENCRYPTION_KEY=
```

Observações:

- `OPENAI_API_KEY` pode ficar vazia e o sistema continua respondendo de forma limitada.
- `CONVERSATION_HASH_KEY` deve ser uma string longa e aleatória.
- `ACCESS_KEYS` usa um JSON com cada chave e seu papel (`support` ou `admin`).
- `BACKUP_ENCRYPTION_KEY` é obrigatório para criar backups criptografados.

## Execução local

```powershell
python run.py
```

A documentação interativa ficará disponível em:

```text
http://127.0.0.1:8000/docs
```

## Exemplo de requisição

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/atendimento/chat -Headers @{"X-API-Key"="sua-chave-de-usuario"} -ContentType 'application/json' -Body '{"sessao_id":"cliente-123","mensagem":"Qual o status do pedido PED-1001?"}'
```

## Segurança

O projeto foi pensado para reduzir risco de vazamento de dados:

- emails, CPF, cartões e dados pessoais são mascarados antes do uso do modelo;
- o conteúdo das conversas não é persistido em texto claro;
- apenas identificadores de sessão protegidos por HMAC são armazenados;
- requisições são limitadas por chave e origem;
- tentativas comuns de prompt injection são encaminhadas sem chamar o modelo.

## Produção

Para ambiente de produção:

- defina `REQUIRE_HTTPS=true`;
- restrinja `ALLOWED_HOSTS` para os domínios reais;
- use um proxy com HTTPS e encaminhamento correto do esquema;
- não execute `run.py` diretamente em produção.

Para gerar um backup cifrado do banco:

```powershell
.\.venv\Scripts\python.exe -m scripts.backup_database
```

Os arquivos gerados em `backups/` devem ser armazenados de forma segura e não versionados.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Licença

Este projeto foi desenvolvido para fins de demonstração e atendimento automatizado, sem compromisso de uso em produção sem revisão adicional de segurança e compliance.