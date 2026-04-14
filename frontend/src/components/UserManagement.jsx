import { useState } from "react";

export function UserManagement({ users, onSubmit, loading }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({ username, password });
    setUsername("");
    setPassword("");
  };

  return (
    <section className="user-grid">
      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Usuarios</p>
            <h2>Adicionar novo usuario</h2>
          </div>
        </div>

        <form className="grid-form compact-two" onSubmit={handleSubmit}>
          <label>
            Usuario
            <input value={username} onChange={(event) => setUsername(event.target.value)} required />
          </label>

          <label>
            Senha
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? "Criando..." : "Criar usuario"}
          </button>
        </form>
      </div>

      <div className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Usuarios</p>
            <h2>Usuarios cadastrados</h2>
          </div>
        </div>

        <div className="user-list">
          {users.map((item) => (
            <div key={item.id} className="user-item">
              <strong>{item.username}</strong>
              <span>ID {item.id}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
