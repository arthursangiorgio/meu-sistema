import { useEffect, useState } from "react";

import { api } from "./api";
import { CategoryForm } from "./components/CategoryForm";
import { DashboardCharts } from "./components/DashboardCharts";
import { LoginForm } from "./components/LoginForm";
import { ReportsView } from "./components/ReportsView";
import { TransactionForm } from "./components/TransactionForm";

const currentMonth = new Date().toISOString().slice(0, 7);

function App() {
  const [user, setUser] = useState(null);
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [report, setReport] = useState(null);
  const [exportInfo, setExportInfo] = useState({ csv_ready: false, pdf_ready: false, message: "" });
  const [month, setMonth] = useState(currentMonth);
  const [tab, setTab] = useState("dashboard");
  const [loadingLogin, setLoadingLogin] = useState(false);
  const [savingTransaction, setSavingTransaction] = useState(false);
  const [savingCategory, setSavingCategory] = useState(false);
  const [error, setError] = useState("");

  const loadBaseData = async (userId, selectedMonth) => {
    const [categoriesData, transactionsData, dashboardData, reportData, exportData] = await Promise.all([
      api.categories(),
      api.transactions(userId, selectedMonth),
      api.dashboard(userId, selectedMonth),
      api.reports(userId, selectedMonth),
      api.exportInfo()
    ]);

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
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingCategory(false);
    }
  };

  const handleDownload = (format) => {
    window.open(api.exportUrl(format, user.id, month), "_blank");
  };

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
        <div>
          <p className="eyebrow">Controle de despesas</p>
          <h1>Ola, {user.username}</h1>
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

      <nav className="tabs">
        <button className={tab === "dashboard" ? "tab active" : "tab"} onClick={() => setTab("dashboard")}>
          Dashboard
        </button>
        <button className={tab === "reports" ? "tab active" : "tab"} onClick={() => setTab("reports")}>
          Relatorios
        </button>
      </nav>

      {dashboard ? (
        <section className="hero-cards">
          <div className="hero-card">
            <span>Saldo atual</span>
            <strong>R$ {dashboard.current_balance.toFixed(2)}</strong>
          </div>
          <div className="hero-card">
            <span>Receitas no mes</span>
            <strong>R$ {dashboard.month_income.toFixed(2)}</strong>
          </div>
          <div className="hero-card">
            <span>Despesas no mes</span>
            <strong>R$ {dashboard.month_expense.toFixed(2)}</strong>
          </div>
        </section>
      ) : null}

      <div className="layout-grid">
        <div className="main-column">
          <TransactionForm
            categories={categories}
            userId={user.id}
            onSubmit={handleCreateTransaction}
            loading={savingTransaction}
          />

          {tab === "dashboard" && dashboard ? <DashboardCharts dashboard={dashboard} /> : null}
          {tab === "reports" && report ? (
            <ReportsView
              report={report}
              exportInfo={exportInfo}
              onDownloadCsv={() => handleDownload("csv")}
              onDownloadPdf={() => handleDownload("pdf")}
            />
          ) : null}
        </div>

        <aside className="side-column">
          <CategoryForm onSubmit={handleCreateCategory} loading={savingCategory} />

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
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

export default App;
