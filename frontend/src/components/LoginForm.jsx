import { useState } from "react";

export function LoginForm({ onLogin, loading }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("1234");

  const handleSubmit = (event) => {
    event.preventDefault();
    onLogin({ username, password });
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <p className="eyebrow">Controle financeiro pessoal</p>
        <h1>Entre e acompanhe suas despesas com clareza</h1>
        <p className="muted">
          Login simples para uso local. Se o usuario nao existir, ele e criado na hora.
        </p>

        <form className="stack" onSubmit={handleSubmit}>
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
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
