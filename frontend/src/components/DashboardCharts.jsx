import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";
import { Bar, Doughnut } from "react-chartjs-2";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export function DashboardCharts({ dashboard }) {
  const pieData = {
    labels: dashboard.by_category.map((item) => item.category),
    datasets: [
      {
        data: dashboard.by_category.map((item) => item.total),
        backgroundColor: dashboard.by_category.map((item) => item.color)
      }
    ]
  };

  const barData = {
    labels: dashboard.by_month.map((item) => item.month),
    datasets: [
      {
        label: "Receitas",
        data: dashboard.by_month.map((item) => item.income),
        backgroundColor: "#177245"
      },
      {
        label: "Despesas",
        data: dashboard.by_month.map((item) => item.expense),
        backgroundColor: "#dc2626"
      }
    ]
  };

  return (
    <section className="chart-grid">
      <div className="panel chart-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h2>Despesas por categoria</h2>
          </div>
        </div>
        {dashboard.by_category.length ? (
          <Doughnut data={pieData} />
        ) : (
          <p className="empty-copy">Cadastre despesas no mes para ver o grafico de pizza.</p>
        )}
      </div>

      <div className="panel chart-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Dashboard</p>
            <h2>Receitas e despesas por mes</h2>
          </div>
        </div>
        {dashboard.by_month.length ? (
          <Bar data={barData} />
        ) : (
          <p className="empty-copy">Adicione lancamentos para alimentar o grafico de barras.</p>
        )}
      </div>
    </section>
  );
}
