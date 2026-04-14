import { useMemo, useState } from "react";

const initialState = {
  description: "",
  amount: "",
  kind: "expense",
  date: new Date().toISOString().slice(0, 10),
  category_id: "",
  notes: ""
};

export function TransactionForm({ categories, userId, onSubmit, loading }) {
  const [form, setForm] = useState(initialState);

  const filteredCategories = useMemo(
    () => categories.filter((category) => category.kind === form.kind),
    [categories, form.kind]
  );

  const handleChange = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: value,
      ...(field === "kind" ? { category_id: "" } : {})
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      ...form,
      amount: Number(form.amount),
      category_id: Number(form.category_id),
      user_id: userId
    });
    setForm((current) => ({
      ...initialState,
      kind: current.kind,
      date: new Date().toISOString().slice(0, 10)
    }));
  };

  return (
    <section className="panel soft-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Lancamentos</p>
          <h2>Nova receita ou despesa</h2>
        </div>
      </div>

      <form className="grid-form" onSubmit={handleSubmit}>
        <label>
          Descricao
          <input
            value={form.description}
            onChange={(event) => handleChange("description", event.target.value)}
            required
          />
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
          Tipo
          <select value={form.kind} onChange={(event) => handleChange("kind", event.target.value)}>
            <option value="expense">Despesa</option>
            <option value="income">Receita</option>
          </select>
        </label>

        <label>
          Categoria
          <select
            value={form.category_id}
            onChange={(event) => handleChange("category_id", event.target.value)}
            required
          >
            <option value="">Selecione</option>
            {filteredCategories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Data
          <input type="date" value={form.date} onChange={(event) => handleChange("date", event.target.value)} required />
        </label>

        <label className="full">
          Observacoes
          <input value={form.notes} onChange={(event) => handleChange("notes", event.target.value)} />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Salvando..." : "Salvar lancamento"}
        </button>
      </form>
    </section>
  );
}
