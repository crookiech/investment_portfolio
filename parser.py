from bs4 import BeautifulSoup
import os
from pathlib import Path

DEFAULT_REPORT_PATH = Path("/mnt/c/уник/ВКР/отчета брокера СБЕР.HTML")
REPORT_PATH_ERROR = True

def html_parse(report_path):
    print("Parsing HTML...")
    with open(report_path) as report:
        soup = BeautifulSoup(report, 'lxml')

        # Поиск периода отчетности
        h3 = soup.find("h3")
        if (h3 and ("за период с" in h3.get_text())):
            reporting_period = h3.get_text(strip=True)
            # извлечение даты
            print(f"Reporting period: {reporting_period}")

        # Поиск даты создания ИИС
        p = soup.find("p")
        if (p and ("Договор на ведение индивидуального инвестиционного счета" in p.get_text())):
            creation_date = p.get_text(strip=True)
            # извлечение даты
            print(f"Creation date: {creation_date}")

        # 

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
            # raise SystemExit(1)
        if (not report_path.exists()):
            print(f"File {report_path} doesn't exist")
            # raise SystemExit(1)
        else:
            REPORT_PATH_ERROR = False    

    _, ext = os.path.splitext(report_path)
    file_format = ext.lower()
    match file_format:
        case ".html":
            print("Starting the parsing HTML")
            html_parse(report_path)
        case _:
            print(f"{file_format} cannot be parsed")
