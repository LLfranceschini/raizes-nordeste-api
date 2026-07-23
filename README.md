# Raízes do Nordeste — API Back-end

## Requisitos
- Python 3.11+
- PostgreSQL 15+

## Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd raizes-nordeste-api
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com seus dados do PostgreSQL
```

### 5. Execute as migrations
```bash
alembic upgrade head
```

### 6. Popule o banco com dados iniciais (seed)
```bash
python -m app.infrastructure.database.seed
```

### 7. Inicie a API
```bash
uvicorn app.main:app --reload
```

### 8. Acesse a documentação (Swagger)
```
http://localhost:8000/docs
```

### 9. Execute os testes
Importe o arquivo `tests/postman_collection.json` no Postman.
