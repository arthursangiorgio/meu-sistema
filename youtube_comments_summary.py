import argparse
import html
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from youtube_comment_downloader import SORT_BY_POPULAR, SORT_BY_RECENT, YoutubeCommentDownloader


STOPWORDS = {
    "a",
    "about",
    "agora",
    "ai",
    "ainda",
    "algo",
    "alguem",
    "algum",
    "alguma",
    "algumas",
    "alguns",
    "all",
    "am",
    "an",
    "and",
    "antes",
    "ao",
    "aos",
    "aqui",
    "are",
    "as",
    "ate",
    "back",
    "bem",
    "by",
    "cada",
    "com",
    "como",
    "da",
    "das",
    "de",
    "del",
    "dela",
    "dele",
    "deles",
    "demais",
    "depois",
    "do",
    "does",
    "dos",
    "e",
    "ela",
    "ele",
    "eles",
    "em",
    "en",
    "entao",
    "era",
    "essa",
    "essas",
    "esse",
    "esses",
    "esta",
    "estas",
    "este",
    "estes",
    "eu",
    "faz",
    "foi",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "hoje",
    "i",
    "if",
    "in",
    "is",
    "isso",
    "isto",
    "ja",
    "la",
    "mais",
    "mas",
    "me",
    "mesmo",
    "meu",
    "minha",
    "muito",
    "na",
    "nas",
    "nem",
    "no",
    "nos",
    "nossa",
    "nosso",
    "not",
    "now",
    "num",
    "o",
    "of",
    "oi",
    "olha",
    "on",
    "once",
    "onde",
    "or",
    "os",
    "ou",
    "para",
    "parece",
    "pela",
    "pelas",
    "pelo",
    "pelos",
    "people",
    "por",
    "pra",
    "que",
    "quem",
    "se",
    "sem",
    "ser",
    "seu",
    "she",
    "so",
    "sobre",
    "some",
    "sua",
    "suas",
    "tambem",
    "te",
    "tem",
    "than",
    "that",
    "the",
    "their",
    "them",
    "there",
    "they",
    "this",
    "to",
    "too",
    "tu",
    "um",
    "uma",
    "umas",
    "uns",
    "very",
    "voces",
    "vocês",
    "voce",
    "você",
    "was",
    "we",
    "what",
    "when",
    "who",
    "why",
    "with",
    "you",
}

POSITIVE_WORDS = {
    "amazing",
    "bom",
    "boa",
    "brabo",
    "excelente",
    "fantastic",
    "genial",
    "good",
    "great",
    "incrivel",
    "incrível",
    "legal",
    "love",
    "loved",
    "maravilhoso",
    "nice",
    "otimo",
    "ótimo",
    "perfeito",
    "top",
}

NEGATIVE_WORDS = {
    "awful",
    "bad",
    "boring",
    "hate",
    "horrible",
    "lixo",
    "meh",
    "odio",
    "ódio",
    "pessimo",
    "péssimo",
    "poor",
    "ruim",
    "terrible",
    "trash",
    "worst",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[@#]\w+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    cleaned = normalize_text(text)
    words = re.findall(r"[a-zA-ZÀ-ÿ']{3,}", cleaned)
    return [word for word in words if word not in STOPWORDS]


def parse_like_count(value) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace(",", ".")
    match = re.match(r"(\d+(?:\.\d+)?)([km]?)", text)
    if not match:
        return 0
    amount = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        amount *= 1_000
    elif suffix == "m":
        amount *= 1_000_000
    return int(amount)


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.lstrip("/") or None
    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        if "v" in query:
            return query["v"][0]
    return None


def fetch_video_title(url: str) -> str:
    try:
        request = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
                )
            },
        )
        with urlopen(request, timeout=15) as response:
            page = response.read().decode("utf-8", errors="ignore")
    except (TimeoutError, URLError, ValueError):
        return "YouTube video"

    match = re.search(r"<title>(.*?)</title>", page, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return "YouTube video"
    title = html.unescape(match.group(1)).replace("- YouTube", "").strip()
    return title or "YouTube video"


def collect_comments(url: str, limit: int, sort_by: str) -> list[dict]:
    downloader = YoutubeCommentDownloader()
    sort_token = SORT_BY_RECENT if sort_by == "recent" else SORT_BY_POPULAR
    comment_stream = downloader.get_comments_from_url(url, sort_by=sort_token)

    comments = []
    for index, comment in enumerate(comment_stream, start=1):
        text = (comment.get("text") or "").strip()
        if not text:
            continue
        comments.append(
            {
                "author": comment.get("author", "Unknown author"),
                "text": text,
                "time": comment.get("time", ""),
                "likes": parse_like_count(comment.get("votes")),
                "reply_count": int(comment.get("reply_count", 0) or 0),
            }
        )
        if index >= limit:
            break
    return comments


def top_ngrams(comments: Iterable[dict], size: int, limit: int) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for comment in comments:
        tokens = tokenize(comment["text"])
        if len(tokens) < size:
            continue
        seen = set()
        for i in range(len(tokens) - size + 1):
            gram = " ".join(tokens[i : i + size])
            if gram in seen:
                continue
            seen.add(gram)
            counter[gram] += 1
    return counter.most_common(limit)


def keyword_counts(comments: Iterable[dict], limit: int = 15) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for comment in comments:
        counts.update(set(tokenize(comment["text"])))
    return counts.most_common(limit)


def classify_sentiment(text: str) -> str:
    tokens = set(tokenize(text))
    positive = len(tokens & POSITIVE_WORDS)
    negative = len(tokens & NEGATIVE_WORDS)
    if positive > negative:
        return "positive"
    if negative > positive:
        return "negative"
    return "neutral"


def representative_comments(comments: list[dict], keywords: list[tuple[str, int]], limit: int = 5) -> list[dict]:
    keyword_set = {keyword for keyword, _ in keywords[:10]}

    ranked = []
    for comment in comments:
        tokens = set(tokenize(comment["text"]))
        richness = len(tokens & keyword_set)
        score = (comment["likes"] * 2) + (comment["reply_count"] * 3) + richness
        ranked.append((score, len(comment["text"]), comment))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in ranked[:limit]]


def build_summary(comments: list[dict]) -> dict:
    sentiments = Counter(classify_sentiment(comment["text"]) for comment in comments)
    keywords = keyword_counts(comments)
    bigrams = top_ngrams(comments, size=2, limit=8)
    trigrams = top_ngrams(comments, size=3, limit=5)

    lengths = [len(comment["text"]) for comment in comments]
    likes = [comment["likes"] for comment in comments]
    authors = {comment["author"] for comment in comments}

    themes = []
    for phrase, count in bigrams[:5]:
        themes.append(f'"{phrase}" aparece em {count} comentários')
    for phrase, count in trigrams[:3]:
        themes.append(f'"{phrase}" reaparece {count} vezes')

    return {
        "comment_count": len(comments),
        "unique_authors": len(authors),
        "avg_length": round(statistics.mean(lengths), 1) if lengths else 0,
        "median_likes": statistics.median(likes) if likes else 0,
        "sentiments": sentiments,
        "keywords": keywords,
        "themes": themes[:6],
        "top_comments": sorted(comments, key=lambda comment: comment["likes"], reverse=True)[:8],
        "representative_comments": representative_comments(comments, keywords),
    }


def render_bar(value: int, max_value: int, color: str) -> str:
    width = 0 if max_value == 0 else max(6, math.ceil((value / max_value) * 100))
    return (
        f'<div class="bar-row"><span>{value}</span>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{width}%;background:{color}"></div></div></div>'
    )


def html_escape(text: str) -> str:
    return html.escape(text, quote=True)


def render_html_report(video_title: str, url: str, summary: dict) -> str:
    sentiments = summary["sentiments"]
    max_sentiment = max(sentiments.values(), default=0)
    max_keyword = max((count for _, count in summary["keywords"]), default=0)

    sentiment_cards = "".join(
        [
            f"""
            <div class="panel">
              <h3>{label}</h3>
              {render_bar(sentiments.get(key, 0), max_sentiment, color)}
            </div>
            """
            for key, label, color in [
                ("positive", "Positivos", "#177245"),
                ("neutral", "Neutros", "#5f6c80"),
                ("negative", "Negativos", "#b63b3b"),
            ]
        ]
    )

    keyword_rows = "".join(
        [
            f"""
            <div class="keyword-row">
              <div class="keyword-label">{html_escape(keyword)}</div>
              {render_bar(count, max_keyword, "#2563eb")}
            </div>
            """
            for keyword, count in summary["keywords"]
        ]
    )

    theme_items = "".join(f"<li>{html_escape(theme)}</li>" for theme in summary["themes"])

    representative_cards = "".join(
        [
            f"""
            <article class="quote-card">
              <p>{html_escape(comment["text"])}</p>
              <footer>{html_escape(comment["author"])} · {comment["likes"]} likes · {comment["reply_count"]} replies</footer>
            </article>
            """
            for comment in summary["representative_comments"]
        ]
    )

    top_comments_rows = "".join(
        [
            f"""
            <tr>
              <td>{html_escape(comment["author"])}</td>
              <td>{comment["likes"]}</td>
              <td>{comment["reply_count"]}</td>
              <td>{html_escape(comment["time"])}</td>
              <td>{html_escape(comment["text"][:200])}</td>
            </tr>
            """
            for comment in summary["top_comments"]
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resumo de comentários do YouTube</title>
  <style>
    :root {{
      --bg: #f5f1e8;
      --card: #fffaf2;
      --ink: #1f2937;
      --muted: #5f6c80;
      --accent: #d97706;
      --border: #e6dcc9;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top right, rgba(217, 119, 6, 0.18), transparent 28%),
        linear-gradient(180deg, #f9f5ee 0%, var(--bg) 100%);
      color: var(--ink);
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 18px 48px;
    }}
    .hero {{
      background: rgba(255, 250, 242, 0.9);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 18px 40px rgba(120, 93, 44, 0.08);
    }}
    h1, h2, h3 {{
      margin: 0 0 12px;
      line-height: 1.1;
    }}
    h1 {{
      font-size: clamp(2rem, 4vw, 3.5rem);
    }}
    p, li, td {{
      font-size: 1rem;
      line-height: 1.6;
    }}
    a {{
      color: #0f4c81;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 24px;
    }}
    .stat-card, .panel, .table-card, .quote-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 12px 30px rgba(120, 93, 44, 0.07);
    }}
    .stat-card strong {{
      display: block;
      font-size: 1.9rem;
      margin-bottom: 6px;
    }}
    .section {{
      margin-top: 28px;
      display: grid;
      gap: 18px;
    }}
    .three-col {{
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    }}
    .two-col {{
      grid-template-columns: 1.1fr 0.9fr;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 48px 1fr;
      align-items: center;
      gap: 12px;
    }}
    .bar-track {{
      width: 100%;
      height: 12px;
      background: #e9e2d3;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
    }}
    .keyword-row {{
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 16px;
      margin-bottom: 14px;
      align-items: center;
    }}
    .keyword-label {{
      font-weight: 700;
      text-transform: capitalize;
    }}
    .quotes {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
    }}
    .quote-card p {{
      margin-top: 0;
      font-size: 1.03rem;
    }}
    .quote-card footer {{
      color: var(--muted);
      font-size: 0.92rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 10px 8px;
      text-align: left;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    th {{
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .muted {{
      color: var(--muted);
    }}
    @media (max-width: 900px) {{
      .two-col {{
        grid-template-columns: 1fr;
      }}
      .keyword-row {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <p class="muted">Resumo automático dos comentários do vídeo</p>
      <h1>{html_escape(video_title)}</h1>
      <p><a href="{html_escape(url)}">{html_escape(url)}</a></p>

      <div class="stats">
        <div class="stat-card"><strong>{summary["comment_count"]}</strong> comentários analisados</div>
        <div class="stat-card"><strong>{summary["unique_authors"]}</strong> autores únicos</div>
        <div class="stat-card"><strong>{summary["avg_length"]}</strong> caracteres por comentário</div>
        <div class="stat-card"><strong>{summary["median_likes"]}</strong> likes medianos</div>
      </div>
    </section>

    <section class="section three-col">
      {sentiment_cards}
    </section>

    <section class="section two-col">
      <div class="table-card">
        <h2>Temas mais recorrentes</h2>
        <ul>{theme_items or "<li>Não houve repetição forte de frases.</li>"}</ul>
      </div>
      <div class="table-card">
        <h2>Palavras-chave</h2>
        {keyword_rows or "<p>Não foi possível identificar palavras-chave suficientes.</p>"}
      </div>
    </section>

    <section class="section">
      <div class="table-card">
        <h2>Comentários representativos</h2>
        <div class="quotes">{representative_cards}</div>
      </div>
    </section>

    <section class="section">
      <div class="table-card">
        <h2>Comentários mais curtidos</h2>
        <table>
          <thead>
            <tr>
              <th>Autor</th>
              <th>Likes</th>
              <th>Replies</th>
              <th>Quando</th>
              <th>Trecho</th>
            </tr>
          </thead>
          <tbody>
            {top_comments_rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def write_report(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa comentários públicos de um vídeo do YouTube e gera um relatório HTML resumido."
    )
    parser.add_argument("url", help="URL do vídeo do YouTube")
    parser.add_argument("--limit", type=int, default=300, help="Número máximo de comentários para analisar")
    parser.add_argument(
        "--sort",
        choices=("popular", "recent"),
        default="popular",
        help="Ordem de coleta dos comentários",
    )
    parser.add_argument(
        "--output",
        default="youtube_comments_report.html",
        help="Arquivo HTML de saída",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print("URL inválida. Use a URL completa do vídeo do YouTube.", file=sys.stderr)
        return 1

    try:
        comments = collect_comments(args.url, args.limit, args.sort)
    except Exception as exc:
        print(f"Falha ao buscar comentários: {exc}", file=sys.stderr)
        return 1

    if not comments:
        print("Nenhum comentário público foi encontrado para esse vídeo.", file=sys.stderr)
        return 1

    summary = build_summary(comments)
    title = fetch_video_title(args.url)
    report_html = render_html_report(title, args.url, summary)

    output_path = Path(args.output).resolve()
    write_report(output_path, report_html)

    print(f"Video: {title}")
    print(f"Video ID: {video_id}")
    print(f"Comentarios analisados: {summary['comment_count']}")
    print(f"Relatorio gerado em: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
