export function ReportsView({ report, exportInfo, onDownloadCsv, onDownloadPdf }) {
  return (
    <section className="report-grid">
      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Relatorios</p>
            <h2>Resumo consolidado</h2>
          </div>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <span>Receitas</span>
            <strong>R$ {report.total_income.toFixed(2)}</strong>
          </div>
          <div className="stat-card">
            <span>Despesas</span>
            <strong>R$ {report.total_expense.toFixed(2)}</strong>
          </div>
          <div className="stat-card">
            <span>Saldo</span>
            <strong>R$ {report.balance.toFixed(2)}</strong>
          </div>
          <div className="stat-card">
            <span>Lancamentos</span>
            <strong>{report.transaction_count}</strong>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Exportacoes futuras</p>
            <h2>Estrutura preparada</h2>
          </div>
        </div>
        <p className="muted">{exportInfo.message}</p>
        <div className="export-pills">
          <button type="button" className={exportInfo.csv_ready ? "pill action-pill active" : "pill action-pill"} onClick={onDownloadCsv}>
            CSV
          </button>
          <button type="button" className={exportInfo.pdf_ready ? "pill action-pill active" : "pill action-pill"} onClick={onDownloadPdf}>
            PDF
          </button>
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Categorias</p>
            <h2>Participacao dos gastos</h2>
          </div>
        </div>

        <div className="category-list">
          {report.categories.length ? (
            report.categories.map((item) => (
              <div key={item.category} className="category-row">
                <div className="category-info">
                  <span className="color-dot" style={{ backgroundColor: item.color }} />
                  <span>{item.category}</span>
                </div>
                <strong>R$ {item.total.toFixed(2)}</strong>
              </div>
            ))
          ) : (
            <p className="empty-copy">Sem despesas para consolidar nesse filtro.</p>
          )}
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Relatorio detalhado</p>
            <h2>Lista de lancamentos</h2>
          </div>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Descricao</th>
                <th>Categoria</th>
                <th>Tipo</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              {report.transactions.map((item) => (
                <tr key={item.id}>
                  <td>{item.date}</td>
                  <td>{item.description}</td>
                  <td>{item.category_name}</td>
                  <td>{item.kind === "income" ? "Receita" : "Despesa"}</td>
                  <td>R$ {item.amount.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
