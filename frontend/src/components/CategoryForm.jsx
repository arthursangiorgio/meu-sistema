import { useState } from "react";

const colors = ["#dc2626", "#f97316", "#2563eb", "#177245", "#7c3aed", "#0891b2"];

export function CategoryForm({ onSubmit, loading }) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState("expense");
  const [color, setColor] = useState(colors[0]);

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({ name, kind, color });
    setName("");
    setKind("expense");
    setColor(colors[0]);
  };

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Categorias</p>
          <h2>Cadastre novos grupos</h2>
        </div>
      </div>

      <form className="grid-form compact" onSubmit={handleSubmit}>
        <label>
          Nome
          <input value={name} onChange={(event) => setName(event.target.value)} required />
        </label>

        <label>
          Tipo
          <select value={kind} onChange={(event) => setKind(event.target.value)}>
            <option value="expense">Despesa</option>
            <option value="income">Receita</option>
          </select>
        </label>

        <label>
          Cor
          <select value={color} onChange={(event) => setColor(event.target.value)}>
            {colors.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Criando..." : "Criar categoria"}
        </button>
      </form>
    </section>
  );
}
