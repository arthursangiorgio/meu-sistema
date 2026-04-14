import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


DEFAULT_TICKER = "005930.KS"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa preços históricos de uma ação e estima o próximo fechamento."
    )
    parser.add_argument(
        "--ticker",
        default=DEFAULT_TICKER,
        help=f"Ticker da ação. Padrão: {DEFAULT_TICKER} (Samsung Electronics)",
    )
    parser.add_argument(
        "--period",
        default="1y",
        help="Janela histórica para download no formato do yfinance, por exemplo 6mo, 1y, 2y.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=5,
        help="Número de fechamentos anteriores usados para prever o próximo.",
    )
    parser.add_argument(
        "--chart",
        default="stock_forecast.png",
        help="Arquivo PNG do gráfico de saída.",
    )
    return parser


def load_history(ticker: str, period: str) -> pd.DataFrame:
    history = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if history.empty:
        raise ValueError(f"Não encontrei dados para o ticker {ticker!r}.")
    if isinstance(history.columns, pd.MultiIndex):
        history.columns = history.columns.get_level_values(0)
    if "Close" not in history.columns:
        raise ValueError("A resposta baixada não trouxe a coluna de fechamento.")
    return history.dropna(subset=["Close"]).copy()


def prepare_training_data(close_prices: pd.Series, window: int) -> tuple[np.ndarray, np.ndarray]:
    values = close_prices.to_numpy(dtype=float)
    if len(values) <= window:
        raise ValueError(
            f"Dados insuficientes: recebi {len(values)} fechamentos, mas preciso de mais de {window}."
        )

    features = []
    targets = []
    for idx in range(window, len(values)):
        features.append(values[idx - window : idx])
        targets.append(values[idx])
    return np.array(features), np.array(targets)


def fit_linear_model(features: np.ndarray, targets: np.ndarray) -> np.ndarray:
    bias = np.ones((features.shape[0], 1))
    design_matrix = np.hstack([bias, features])
    coefficients, *_ = np.linalg.lstsq(design_matrix, targets, rcond=None)
    return coefficients


def predict_next_close(close_prices: pd.Series, window: int) -> tuple[float, float, np.ndarray]:
    features, targets = prepare_training_data(close_prices, window)
    coefficients = fit_linear_model(features, targets)

    bias = coefficients[0]
    weights = coefficients[1:]

    latest_window = close_prices.to_numpy(dtype=float)[-window:]
    prediction = float(bias + np.dot(latest_window, weights))

    training_predictions = np.hstack([np.nan] * window + list(features @ weights + bias))
    return prediction, float(close_prices.iloc[-1]), training_predictions


def directional_hint(prediction: float, last_close: float) -> str:
    delta = prediction - last_close
    pct = (delta / last_close) * 100 if last_close else 0.0
    direction = "alta" if delta > 0 else "queda" if delta < 0 else "estabilidade"
    return f"{direction} estimada de {pct:.2f}%"


def save_chart(history: pd.DataFrame, training_predictions: np.ndarray, prediction: float, chart_path: Path) -> None:
    recent = history.tail(60).copy()
    recent_predictions = training_predictions[-len(recent) :]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6))

    ax.plot(recent.index, recent["Close"], label="Fechamento real", linewidth=2.3, color="#0f4c81")
    ax.plot(recent.index, recent_predictions, label="Ajuste do modelo", linewidth=1.8, color="#d97706")
    ax.scatter([recent.index[-1]], [prediction], s=120, color="#177245", label="Próximo fechamento previsto", zorder=3)

    ax.set_title("Previsão simples do próximo fechamento")
    ax.set_ylabel("Preço")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        history = load_history(args.ticker, args.period)
        close_prices = history["Close"]
        prediction, last_close, training_predictions = predict_next_close(close_prices, args.window)
    except Exception as exc:
        print(f"Erro: {exc}")
        return 1

    chart_path = Path(args.chart).resolve()
    save_chart(history, training_predictions, prediction, chart_path)

    last_date = history.index[-1]
    next_hint = directional_hint(prediction, last_close)

    print(f"Ticker: {args.ticker}")
    print(f"Último pregão disponível: {last_date:%Y-%m-%d}")
    print(f"Último fechamento ajustado: {last_close:.2f}")
    print(f"Próximo fechamento previsto: {prediction:.2f}")
    print(f"Sinal do modelo: {next_hint}")
    print(f"Gráfico salvo em: {chart_path}")
    print("Aviso: isso é uma previsão estatística simples, não uma recomendação de investimento.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
