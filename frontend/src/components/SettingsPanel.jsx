import { useEffect, useMemo, useState } from "react";

const emptySettings = {
  default_income_description: "",
  default_expense_description: "",
  default_income_category_id: "",
  default_expense_category_id: ""
};

export function SettingsPanel({ categories, settings, onSubmit, loading }) {
  const [form, setForm] = useState(emptySettings);

  useEffect(() => {
    setForm({
      default_income_description: settings?.default_income_description || "",
      default_expense_description: settings?.default_expense_description || "",
      default_income_category_id: settings?.default_income_category_id?.toString() || "",
      default_expense_category_id: settings?.default_expense_category_id?.toString() || ""
    });
  }, [settings]);

  const incomeCategories = useMemo(
    () => categories.filter((category) => category.kind === "income"),
    [categories]
  );
  const expenseCategories = useMemo(
    () => categories.filter((category) => category.kind === "expense"),
    [categories]
  );

  const handleChange = (field, value) => {
    setForm((current) => ({
      ...current,
      [field]: value
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      default_income_description: form.default_income_description,
      default_expense_description: form.default_expense_description,
      default_income_category_id: form.default_income_category_id ? Number(form.default_income_category_id) : null,
      default_expense_category_id: form.default_expense_category_id ? Number(form.default_expense_category_id) : null
    });
  };

  return (
    <section className="settings-grid">
      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Configuracao</p>
            <h2>Padroes do lancamento</h2>
            <p className="muted panel-copy">
              Se a descricao ficar vazia, o sistema usa o padrao salvo aqui. Sem padrao, continua usando
              &quot;Receita&quot; e &quot;Despesa&quot;.
            </p>
          </div>
        </div>

        <form className="grid-form" onSubmit={handleSubmit}>
          <label>
            Descricao padrao da receita
            <input
              value={form.default_income_description}
              onChange={(event) => handleChange("default_income_description", event.target.value)}
              placeholder='Exemplo: Entrada'
            />
          </label>

          <label>
            Categoria padrao da receita
            <select
              value={form.default_income_category_id}
              onChange={(event) => handleChange("default_income_category_id", event.target.value)}
            >
              <option value="">Selecione</option>
              {incomeCategories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Descricao padrao da despesa
            <input
              value={form.default_expense_description}
              onChange={(event) => handleChange("default_expense_description", event.target.value)}
              placeholder='Exemplo: Gasto'
            />
          </label>

          <label>
            Categoria padrao da despesa
            <select
              value={form.default_expense_category_id}
              onChange={(event) => handleChange("default_expense_category_id", event.target.value)}
            >
              <option value="">Selecione</option>
              {expenseCategories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Salvando..." : "Salvar configuracao"}
          </button>
        </form>
      </div>
    </section>
  );
}
