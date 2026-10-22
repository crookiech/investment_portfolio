from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, date
from pydantic import BaseModel, ValidationError
import requests
import os
import re

DEFAULT_REPORT_PATH = Path("/mnt/c/уник/ВКР/отчет брокера СБЕР.HTML")
REPORT_PATH_ERROR = True

def to_float(s: str, default: float | None = None) -> float | None:
    s = s.replace("\xa0", "").replace(" ", "").replace(",", ".")
    if not s:
        return default
    return float(s)

def to_int(s: str, default: int | None = None) -> int | None:
    v = to_float(s, default=None)
    return default if v is None else int(v)

def to_date(s: str) -> date:
    return datetime.strptime(s, "%d.%m.%Y").date()

class Security(BaseModel):
    name: str
    isin: str
    currency: str
    number: int
    nominal_val: float | None
    price: float # цена
    value: float # стоимость

class Report(BaseModel):
    start_reporting_period: date
    end_reporting_period: date
    creation_date: date
    securities: list[Security]

def securities_parse(soup: BeautifulSoup) -> list[Security]:
    securities: list[Security] = []
    for table in soup.find_all("table"):
        if ("Наименование" not in table.get_text()):
            continue
        for tr in table.find_all("tr"):
            if (set(tr.get("class") or []) & {"table-header", "rn"}):
                continue
            tds = tr.find_all("td")
            if ((len(tds) != 18) or tds[0].get_text(strip=True).isdigit()):
                continue
            row = [td.get_text(strip=True) for td in tds]
            try:
                securities.append(Security(
                    name=row[0],
                    isin=row[1],
                    currency=row[2],
                    number=to_int(row[3]),
                    nominal_val=to_float(row[4]),
                    price=to_float(row[5]),
                    value=to_float(row[6]),
                ))
            except ValidationError as e:
                print(f"Error: {e}")
    return securities

def report_parse(soup: BeautifulSoup) -> Report:
    # Поиск периода отчетности
    start_reporting_period = None
    end_reporting_period = None
    for h3 in soup.find_all("h3"):
        text = h3.get_text(" ", strip=True)
        if "за период с" in text:
            dates = re.search(r"с\s+(\d{2}\.\d{2}\.\d{4})\s+по\s+(\d{2}\.\d{2}\.\d{4})", text)
            if dates:
                start_reporting_period = to_date(dates.group(1))
                end_reporting_period = to_date(dates.group(2))
            break

    # Поиск даты создания ИИС
    creation_date = None
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if ("Договор на ведение индивидуального инвестиционного счета" not in text):
            continue
        date = re.search(r"от\s+(\d{2}\.\d{2}\.\d{4})", text)
        if date:
            creation_date = to_date(date.group(1))
        break

    securities: list[Security] = securities_parse(soup)

    try:
        return Report(
            start_reporting_period = start_reporting_period,
            end_reporting_period = end_reporting_period,
            creation_date = creation_date,
            securities = securities,
        )
    except ValueError as e:
        print(f"Error: {e}")
        return None

def html_parse(report_path) -> Report:
    print("Parsing HTML...")
    raw = Path(report_path).read_bytes()
    soup = BeautifulSoup(raw, "lxml")

    report: Report = report_parse(soup)

    return report

def get_current_usd_rate() -> float:
    url = "https://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')
    for valute in soup.find_all("Valute"):
        char_code = valute.find("CharCode")
        if (char_code.text == "USD"):
            value = valute.find("Value")
    return float(value.text.replace(",", "."))

def calc_investment_portfolio_value(report: Report, usd_rate: float) -> float:
    value_RUB = [security.value for security in report.securities if security.currency == "RUB"]
    value_USD = [(security.value * usd_rate) for security in report.securities if security.currency == "USD"]
    value = sum(value_RUB) + sum(value_USD)
    return value

def calc_share_asset_in_investment_portfolio(report: Report, usd_rate: float) -> dict:
    weights = {}
    asset_RUB = [security.value for security in report.securities if security.currency == "RUB"]
    asset_USD = [(security.value * usd_rate) for security in report.securities if security.currency == "USD"]
    asset_value = sum(asset_RUB) + sum(asset_USD)
    for security in report.securities:
        value_rub = security.value * (usd_rate if security.currency == "USD" else 1.0)
        weights[security.name] = value_rub / asset_value
    return weights

def parse(report_path: Path) -> Report | None:
    if not report_path.exists():
        print(f"File {report_path} doesn't exist")
        return None
    if report_path.is_dir():
        print(f"{report_path} is a directory")
        return None

    match report_path.suffix.lower():
        case ".html":
            print("Starting the parsing HTML")
            return html_parse(report_path)
        case _:
            print(f"{report_path.suffix} cannot be parsed")
            return None

if __name__ == "__main__":
    while(REPORT_PATH_ERROR):
        user_input = input("Enter the path to the brokerage report: ").strip().strip('"')
        if not user_input:
            report_path = DEFAULT_REPORT_PATH
        else:
            report_path = Path(user_input)

        print(f"Path to the brokerage report: {report_path}")

        if (report_path.is_dir()):
            print(f"{report_path} is a directory")
        if (not report_path.exists()):
            print(f"File {report_path} doesn't exist")
        else:
            REPORT_PATH_ERROR = False    

    _, ext = os.path.splitext(report_path)
    file_format = ext.lower()
    match file_format:
        case ".html":
            print("Starting the parsing HTML")
            report = html_parse(report_path)
            print(report)
            usd_rate = get_current_usd_rate()
            print(f"Dollar exchange rate: {usd_rate}")
            print(calc_investment_portfolio_value(report, usd_rate))
            print(calc_share_asset_in_investment_portfolio(report, usd_rate))
        case _:
            print(f"{file_format} cannot be parsed")
