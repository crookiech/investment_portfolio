import tempfile
import pathlib
import pandas as pd
import plotly.express as px
import streamlit
from parser import parse, get_current_usd_rate, calc_investment_portfolio_value, calc_share_asset_in_investment_portfolio

streamlit.set_page_config(page_title="Инвестиционный портфель", layout="wide")
streamlit.title("Структура инвестиционного портфеля")

@streamlit.cache_data(show_spinner="Парсим отчёт…")
def parse_uploaded(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        tmp.write(file_bytes)
        tmp_path = pathlib.Path(tmp.name)
    return parse(tmp_path)


@streamlit.cache_data(ttl=3600, show_spinner="Получаем курс ЦБ РФ…")
def cbr_rate() -> float:
    return get_current_usd_rate()

with streamlit.sidebar:
    uploaded = streamlit.file_uploader("Отчёт брокера", type=["html", "htm"])
    try:
        usd_rate = cbr_rate()
        streamlit.success(f"Курс доллара (ЦБ РФ): {usd_rate:.4f} ₽")
    except Exception as e:
        streamlit.error(f"Не удалось получить курс: {e}")


if uploaded is None:
    streamlit.info("Загрузите отчёт брокера в боковой панели")
    streamlit.stop()

try:
    report = parse_uploaded(uploaded.getvalue())
except Exception as e:
    streamlit.error(f"Ошибка парсинга: {e}")
    streamlit.stop()

if report is None:
    streamlit.error("Не удалось распарсить отчёт")
    streamlit.stop()

total = calc_investment_portfolio_value(report, usd_rate)
weights = calc_share_asset_in_investment_portfolio(report, usd_rate)

c1, c2 = streamlit.columns(2)
c1.metric("Стоимость портфеля", f"{total:,.2f} ₽")
c2.metric("Период отчёта", f"{report.start_reporting_period:%d.%m.%Y} – {report.end_reporting_period:%d.%m.%Y}")

df = pd.DataFrame(
    {"Бумага": list(weights.keys()), "Доля": list(weights.values())}
).sort_values("Доля", ascending=False)

fig = px.pie(
    df,
    names="Бумага",
    values="Доля",
    hole=0.45,
)
fig.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>%{label}</b><br>Доля: %{percent}<extra></extra>",
)
fig.update_layout(
    legend=dict(orientation="v", yanchor="middle", y=0.5),
    margin=dict(t=60, b=20, l=20, r=20),
    height=600,
)

streamlit.plotly_chart(fig, use_container_width=True)

detail = pd.DataFrame([
    {
        "Бумага": s.name,
        "ISIN": s.isin,
        "Валюта": s.currency,
        "Кол-во": s.number,
        "Цена": s.price,
        "Стоимость (вал.)": s.value,
        "Стоимость (₽)": s.value * (usd_rate if s.currency == "USD" else 1.0),
        "Доля, %": weights[s.name] * 100,
    }
    for s in report.securities
]).sort_values("Доля, %", ascending=False)

streamlit.dataframe(
    detail,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Стоимость (вал.)": streamlit.column_config.NumberColumn(format="%.2f"),
        "Стоимость (₽)": streamlit.column_config.NumberColumn(format="%.2f ₽"),
        "Доля, %": streamlit.column_config.ProgressColumn(
            format="%.2f%%", min_value=0, max_value=100
        ),
    },
)
