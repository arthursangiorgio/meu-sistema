import { useEffect, useState } from "react";

import { api } from "./api";
import { CategoryForm } from "./components/CategoryForm";
import { DashboardCharts } from "./components/DashboardCharts";
import { LoginForm } from "./components/LoginForm";
import { ReportsView } from "./components/ReportsView";
import { TransactionForm } from "./components/TransactionForm";
import { UserManagement } from "./components/UserManagement";

const currentMonth = new Date().toISOString().slice(0, 7);

function App() {
  const [user, setUser] = useState(null);
  const [categories, setCategories] = useState([]);
  const [users, setUsers] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [report, setReport] = useState(null);
  const [exportInfo, setExportInfo] = useState({ csv_ready: false, pdf_ready: false, message: "" });
  const [month, setMonth] = useState(currentMonth);
  const [tab, setTab] = useState("summary");
  const [loadingLogin, setLoadingLogin] = useState(false);
  const [savingTransaction, setSavingTransaction] = useState(false);
  const [savingCategory, setSavingCategory] = useState(false);
  const [savingUser, setSavingUser] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadBaseData = async (userId, selectedMonth) => {
    const [usersData, categoriesData, transactionsData, dashboardData, reportData, exportData] = await Promise.all([
      api.users(),
      api.categories(),
      api.transactions(userId, selectedMonth),
      api.dashboard(userId, selectedMonth),
      api.reports(userId, selectedMonth),
      api.exportInfo()
    ]);

    setUsers(usersData);
    setCategories(categoriesData);
    setTransactions(transactionsData);
    setDashboard(dashboardData);
    setReport(reportData);
    setExportInfo(exportData);
  };

  useEffect(() => {
    if (!user) {
      return;
    }
    loadBaseData(user.id, month).catch((err) => setError(err.message));
  }, [user, month]);

  useEffect(() => {
    if (!notice) {
      return;
    }
    const timer = window.setTimeout(() => setNotice(""), 2600);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const handleLogin = async (credentials) => {
    try {
      setLoadingLogin(true);
      setError("");
      const loggedUser = await api.login(credentials);
      setUser(loggedUser);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingLogin(false);
    }
  };

  const handleCreateTransaction = async (payload) => {
    try {
      setSavingTransaction(true);
      setError("");
      await api.createTransaction(payload);
      await loadBaseData(user.id, month);
      setNotice("Lancamento salvo com sucesso.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingTransaction(false);
    }
  };

  const handleCreateCategory = async (payload) => {
    try {
      setSavingCategory(true);
      setError("");
      await api.createCategory(payload);
      await loadBaseData(user.id, month);
      setNotice("Categoria criada com sucesso.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingCategory(false);
    }
  };

  const handleDeleteTransaction = async (transaction) => {
    const confirmed = window.confirm(`Excluir o lancamento "${transaction.description}"?`);
    if (!confirmed) {
      return;
    }

    try {
      setError("");
      await api.deleteTransaction(transaction.id);
      await loadBaseData(user.id, month);
      setNotice("Lancamento excluido com sucesso.");
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDownload = (format) => {
    window.open(api.exportUrl(format, user.id, month), "_blank");
    setNotice(`Download de ${format.toUpperCase()} iniciado.`);
  };

  const handleCreateUser = async (payload) => {
    try {
      setSavingUser(true);
      setError("");
      await api.createUser(payload);
      await loadBaseData(user.id, month);
      setNotice("Usuario criado com sucesso.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingUser(false);
    }
  };

  const handleDeleteUser = async (targetUser) => {
    const confirmed = window.confirm(`Excluir o usuario "${targetUser.username}"?`);
    if (!confirmed) {
      return;
    }

    try {
      setError("");
      await api.deleteUser(targetUser.id);
      if (targetUser.id === user.id) {
        setUser(null);
        setNotice("");
        return;
      }
      await loadBaseData(user.id, month);
      setNotice("Usuario excluido com sucesso.");
    } catch (err) {
      setError(err.message);
    }
  };

  const summaryCards = dashboard ? (
    <section className="hero-cards">
      <div className="hero-card primary">
        <span>Saldo atual</span>
        <strong>R$ {dashboard.current_balance.toFixed(2)}</strong>
        <small>Visao geral acumulada</small>
      </div>
      <div className="hero-card">
        <span>Receitas no mes</span>
        <strong>R$ {dashboard.month_income.toFixed(2)}</strong>
        <small>Entradas do periodo filtrado</small>
      </div>
      <div className="hero-card">
        <span>Despesas no mes</span>
        <strong>R$ {dashboard.month_expense.toFixed(2)}</strong>
        <small>Saidas do periodo filtrado</small>
      </div>
    </section>
  ) : null;

  const recentTransactionsPanel = (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Ultimos lancamentos</p>
          <h2>Movimentacoes recentes</h2>
        </div>
      </div>

      <div className="timeline">
        {transactions.slice(0, 8).map((item) => (
          <div key={item.id} className="timeline-item">
            <div className="timeline-top">
              <strong>{item.description}</strong>
              <span className={item.kind === "income" ? "badge income" : "badge expense"}>
                {item.kind === "income" ? "Receita" : "Despesa"}
              </span>
            </div>
            <p>{item.category_name}</p>
            <div className="timeline-bottom">
              <span>{item.date}</span>
              <strong>R$ {item.amount.toFixed(2)}</strong>
            </div>
            <button
              type="button"
              className="danger-button subtle timeline-action"
              onClick={() => handleDeleteTransaction(item)}
            >
              Excluir lancamento
            </button>
          </div>
        ))}
      </div>
    </section>
  );

  if (!user) {
    return (
      <>
        {error ? <div className="alert">{error}</div> : null}
        <LoginForm onLogin={handleLogin} loading={loadingLogin} />
      </>
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-copy">
          <p className="eyebrow">Controle de despesas</p>
          <h1>Ola, {user.username}</h1>
          <p className="hero-subtitle">
            Painel simples para acompanhar saldo, movimentacoes e relatorios em um unico lugar.
          </p>
        </div>

        <div className="topbar-actions">
          <label className="month-filter">
            Mes
            <input type="month" value={month} onChange={(event) => setMonth(event.target.value)} />
          </label>
          <button className="ghost-button" onClick={() => setUser(null)}>
            Sair
          </button>
        </div>
      </header>

      {error ? <div className="alert">{error}</div> : null}
      {notice ? <div className="notice">{notice}</div> : null}

      <nav className="tabs">
        <button className={tab === "summary" ? "tab active" : "tab"} onClick={() => setTab("summary")}>
          Resumo
        </button>
        <button className={tab === "dashboard" ? "tab active" : "tab"} onClick={() => setTab("dashboard")}>
          Dashboard
        </button>
        <button className={tab === "reports" ? "tab active" : "tab"} onClick={() => setTab("reports")}>
          Relatorios
        </button>
        <button className={tab === "categories" ? "tab active" : "tab"} onClick={() => setTab("categories")}>
          Categorias
        </button>
        <button className={tab === "users" ? "tab active" : "tab"} onClick={() => setTab("users")}>
          Usuarios
        </button>
      </nav>

      {tab === "summary" ? (
        <>
          {summaryCards}

          <div className="layout-grid summary-layout">
            <div className="main-column summary-form-column">
              <TransactionForm
                categories={categories}
                userId={user.id}
                onSubmit={handleCreateTransaction}
                loading={savingTransaction}
              />
            </div>

            <aside className="side-column summary-history-column">
              {recentTransactionsPanel}
            </aside>
          </div>
        </>
      ) : null}

      {tab === "dashboard" && dashboard ? (
        <>
          {summaryCards}
          <div className="layout-grid">
            <div className="main-column">
              <DashboardCharts dashboard={dashboard} />
            </div>
            <aside className="side-column">
              {recentTransactionsPanel}
            </aside>
          </div>
        </>
      ) : null}
      {tab === "reports" && report ? (
        <ReportsView
          report={report}
          exportInfo={exportInfo}
          onDeleteTransaction={handleDeleteTransaction}
          onDownloadCsv={() => handleDownload("csv")}
          onDownloadPdf={() => handleDownload("pdf")}
        />
      ) : null}
      {tab === "categories" ? (
        <CategoryForm categories={categories} onSubmit={handleCreateCategory} loading={savingCategory} />
      ) : null}
      {tab === "users" ? (
        <UserManagement
          users={users}
          currentUserId={user.id}
          onSubmit={handleCreateUser}
          onDelete={handleDeleteUser}
          loading={savingUser}
        />
      ) : null}
    </div>
  );
}

export default App;
