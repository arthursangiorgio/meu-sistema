import { useState } from "react";

const initialState = {
  title: "",
  client_name: "",
  amount: "",
  status: "pending",
  service_date: new Date().toISOString().slice(0, 10),
  received_date: "",
  notes: ""
};

export function ServicesPanel({ services, summary, userId, onCreate, onToggleStatus, onDelete, loading }) {
  const [form, setForm] = useState(initialState);

  const handleChange = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: value,
      ...(field === "status" && value === "pending" ? { received_date: "" } : {})
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onCreate({
      ...form,
      amount: Number(form.amount),
      received_date: form.status === "received" ? (form.received_date || form.service_date) : null,
      user_id: userId
    });
    setForm(initialState);
  };

  return (
    <section className="services-layout">
      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Servicos</p>
            <h2>Novo servico</h2>
            <p className="muted panel-copy">Cadastre trabalhos pendentes ou recebidos sem misturar com lancamentos manuais.</p>
          </div>
        </div>

        <form className="grid-form" onSubmit={handleSubmit}>
          <label>
            Nome do servico
            <input value={form.title} onChange={(event) => handleChange("title", event.target.value)} required />
          </label>

          <label>
            Cliente
            <input value={form.client_name} onChange={(event) => handleChange("client_name", event.target.value)} />
          </label>

          <label>
            Valor
            <input
              type="number"
              step="0.01"
              value={form.amount}
              onChange={(event) => handleChange("amount", event.target.value)}
              required
            />
          </label>

          <label>
            Status
            <select value={form.status} onChange={(event) => handleChange("status", event.target.value)}>
              <option value="pending">Pendente</option>
              <option value="received">Recebido</option>
            </select>
          </label>

          <label>
            Data do servico
            <input
              type="date"
              value={form.service_date}
              onChange={(event) => handleChange("service_date", event.target.value)}
              required
            />
          </label>

          <label>
            Data de recebimento
            <input
              type="date"
              value={form.received_date}
              onChange={(event) => handleChange("received_date", event.target.value)}
              disabled={form.status !== "received"}
            />
          </label>

          <label className="full">
            Observacoes
            <input value={form.notes} onChange={(event) => handleChange("notes", event.target.value)} />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Salvando..." : "Salvar servico"}
          </button>
        </form>
      </div>

      <div className="service-summary-grid">
        <div className="hero-card primary compact-service-card">
          <span>Recebido no periodo</span>
          <strong>R$ {summary.received_amount.toFixed(2)}</strong>
          <small>Ja entra no calculo da receita.</small>
        </div>
        <div className="hero-card compact-service-card">
          <span>Pendente no periodo</span>
          <strong>R$ {summary.pending_amount.toFixed(2)}</strong>
          <small>Valor ainda aguardando recebimento.</small>
        </div>
        <div className="hero-card compact-service-card">
          <span>Servicos cadastrados</span>
          <strong>{summary.total_services}</strong>
          <small>Quantidade total filtrada.</small>
        </div>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Servicos</p>
            <h2>Lista de servicos</h2>
          </div>
        </div>

        <div className="service-list">
          {services.length ? (
            services.map((item) => (
              <div key={item.id} className="service-item">
                <div className="timeline-top">
                  <div>
                    <strong>{item.title}</strong>
                    <p className="muted service-client">{item.client_name || "Sem cliente informado"}</p>
                  </div>
                  <span className={item.status === "received" ? "badge income" : "badge pending"}>
                    {item.status === "received" ? "Recebido" : "Pendente"}
                  </span>
                </div>

                <div className="service-meta-grid">
                  <span>Servico: {item.service_date}</span>
                  <span>Recebimento: {item.received_date || "Ainda nao recebido"}</span>
                  <strong>R$ {item.amount.toFixed(2)}</strong>
                </div>

                {item.notes ? <p className="service-notes">{item.notes}</p> : null}

                <div className="service-actions">
                  <button
                    type="button"
                    className="ghost-action"
                    onClick={() => onToggleStatus(item)}
                  >
                    {item.status === "received" ? "Voltar para pendente" : "Marcar como recebido"}
                  </button>
                  <button type="button" className="danger-button subtle" onClick={() => onDelete(item)}>
                    Excluir
                  </button>
                </div>
              </div>
            ))
          ) : (
            <p className="empty-copy">Nenhum servico cadastrado nesse periodo.</p>
          )}
        </div>
      </div>
    </section>
  );
}
