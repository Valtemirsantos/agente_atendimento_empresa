# Agente de Atendimento da Empresa

API em Python para atendimento a clientes, com FastAPI, Agno e OpenAI. O agente consulta produtos e pedidos por ferramentas locais e encaminha temas sensiveis a uma pessoa atendente.

## Requisitos

- Python 3.12 ou superior
- Uma chave da API OpenAI para respostas geradas pelo agente

## Execucao

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha `OPENAI_API_KEY`, uma `CONVERSATION_HASH_KEY` longa e aleatoria e uma chave de acesso em `ACCESS_KEYS` no arquivo `.env` e inicie a API. Cada chave de acesso deve receber o papel `support` ou `admin`.

```powershell
python run.py
```

A documentacao interativa estara em `http://127.0.0.1:8000/docs`.

## Exemplo

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/atendimento/chat -Headers @{"X-API-Key"="sua-chave-de-usuario"} -ContentType 'application/json' -Body '{"sessao_id":"cliente-123","mensagem":"Qual o status do pedido PED-1001?"}'
```

Sem `OPENAI_API_KEY`, a rota continua respondendo e encaminha o caso ao atendimento humano. E-mails, CPF e cartoes sao redigidos antes do envio a OpenAI. O conteudo das conversas nao e persistido; apenas um identificador de sessao protegido por HMAC e armazenado por, no maximo, `CONVERSATION_RETENTION_DAYS` dias. Requisicoes sao limitadas por chave e origem e tentativas comuns de prompt injection sao encaminhadas sem chamar o modelo.

## Producao

Defina `REQUIRE_HTTPS=true` e publique atras de um proxy que entregue HTTPS e repasse o esquema correto para a aplicacao. Restrinja `ALLOWED_HOSTS` aos dominios reais. Nao use `run.py` diretamente em producao.

Para gerar um backup cifrado, configure uma chave Fernet em `BACKUP_ENCRYPTION_KEY` e execute:

```powershell
 .\.venv\Scripts\python.exe -m scripts.backup_database
```

O arquivo produzido em `backups/` e criptografado e nao deve ser versionado. Execute os testes com `pytest`.