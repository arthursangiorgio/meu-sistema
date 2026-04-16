import { useEffect, useMemo, useState } from "react";

const initialState = {
  description: "",
  amount: "",
  kind: "expense",
  date: new Date().toISOString().slice(0, 10),
  category_id: "",
  notes: ""
};

const quickAmounts = [1, 5, 10, 25, 50, 100];

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL"
});

export function TransactionForm({ categories, settings, userId, onSubmit, loading }) {
  const [form, setForm] = useState(initialState);

  const filteredCategories = useMemo(
    () => categories.filter((category) => category.kind === form.kind),
    [categories, form.kind]
  );

  const defaultCategoryId = useMemo(() => {
    if (form.kind === "income") {
      return settings?.default_income_category_id?.toString() || "";
    }
    return settings?.default_expense_category_id?.toString() || "";
  }, [form.kind, settings]);

  const handleChange = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: value,
      ...(field === "kind" ? { category_id: "" } : {})
    }));
  };

  const handleQuickAmount = (increment) => {
    const currentAmount = Number(form.amount) || 0;
    const nextAmount = currentAmount + increment;
    handleChange("amount", nextAmount.toFixed(2));
  };

  const amountPreview = Number(form.amount) || 0;
  const descriptionPlaceholder =
    form.kind === "income"
      ? settings?.default_income_description || "Receita"
      : settings?.default_expense_description || "Despesa";

  useEffect(() => {
    const currentCategoryIsValid = filteredCategories.some((category) => String(category.id) === form.category_id);

    if (!form.category_id && defaultCategoryId) {
      setForm((current) => ({
        ...current,
        category_id: defaultCategoryId
      }));
      return;
    }

    if (form.category_id && !currentCategoryIsValid) {
      setForm((current) => ({
        ...current,
        category_id: defaultCategoryId
      }));
    }
  }, [defaultCategoryId, filteredCategories, form.category_id]);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      ...form,
      description: form.description.trim(),
      amount: Number(form.amount),
      category_id: Number(form.category_id),
      user_id: userId
    });
    setForm((current) => ({
      ...initialState,
      kind: current.kind,
      category_id: defaultCategoryId,
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
            placeholder={`Se deixar vazio, salva como "${descriptionPlaceholder}"`}
          />
        </label>

        <label className="full">
          Valor
          <input
            type="number"
            step="0.01"
            value={form.amount}
            onChange={(event) => handleChange("amount", event.target.value)}
            required
          />

          <div className="amount-panel">
            <div className="amount-panel-copy">
              <span>Valor acumulado</span>
              <strong>{currencyFormatter.format(amountPreview)}</strong>
              <small>Toque nos atalhos para ir somando rapidamente.</small>
            </div>

            <div className="quick-amount-grid">
              {quickAmounts.map((value) => (
                <button
                  key={value}
                  type="button"
                  className="quick-amount-button"
                  onClick={() => handleQuickAmount(value)}
                >
                  +{value}
                </button>
              ))}
            </div>
          </div>
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
