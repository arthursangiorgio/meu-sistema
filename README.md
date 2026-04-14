# Sistema Web de Controle de Despesas

Projeto completo e simples com:

- Frontend: React + Vite
- Backend: FastAPI
- Banco: SQLite local
- Graficos: Chart.js

## Estrutura

```text
backend/
  app/
    __init__.py
    database.py
    main.py
    models.py
    schemas.py
    seed.py
    services.py
  requirements.txt
frontend/
  src/
    components/
      CategoryForm.jsx
      DashboardCharts.jsx
      LoginForm.jsx
      ReportsView.jsx
      TransactionForm.jsx
    api.js
    App.jsx
    main.jsx
    styles.css
  index.html
  package.json
  vite.config.js
README.md
```

## Funcionalidades iniciais

- Login local simples
- Cadastro de receitas e despesas
- Cadastro de categorias
- Filtro por mes
- Exibicao de saldo atual
- Dashboard com grafico de pizza por categoria
- Dashboard com grafico de barras por mes
- Tela de relatorios
- Estrutura pronta para exportacao futura em CSV e PDF

## Como rodar o backend

```bash
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Usuario inicial criado automaticamente:

```text
usuario: admin
senha: 1234
```

## Como rodar o frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

## Fluxo basico

1. Faca login com `admin / 1234`.
2. Cadastre receitas e despesas.
3. Use o filtro de mes para navegar entre periodos.
4. Veja os graficos no dashboard.
5. Abra a aba de relatorios para o resumo detalhado.

## Observacoes

- O banco SQLite e criado automaticamente em `backend/expense_control.db`.
- A autenticacao e propositalmente simples e local.
- A exportacao CSV/PDF ainda nao foi implementada, mas a estrutura de API e interface ja esta preparada.
