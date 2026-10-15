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


        # ДАЛЬШЕ ВСЁ ФИГНЯ, НАДО ИСКАТЬ ПО СТРОКАМ (собирать инфу по наименованию)
        # Список ISINов
        ## наверное лучше хранить в словаре
        isins = set()
        for table in soup.find_all("table"):
            if "ISIN" not in table.get_text():
                continue
            isin_col = None
            for tr in table.find_all("tr", class_="table-header"):
                if "ISIN" in tr.get_text():
                    for idx, td in enumerate(tr.find_all("td")):
                        if "ISIN" in td.get_text():
                            isin_col = idx
                            break
                    break
            if isin_col is None:
                continue
            for tr in table.find_all("tr"):
                td = tr.find_all("td")
                if (len(td) > isin_col):
                    text = td[isin_col].get_text(strip=True)
                    if (len(text)==12):
                        isins.add(text)
        print(isins)

        # Количество ценных бумаг (первое попавшееся количество)
        share_number = set()
        for table in soup.find_all("table"):
            if ("Количество" not in table.get_text()):
                continue
            share_number_col = None
            for tr in table.find_all("tr", class_="table-header"):
                for idx, td in enumerate(tr.find_all("td")):
                    if ("Количество" in td.get_text()):
                        share_number_col = idx
                        break
                if share_number_col is not None:
                    break
            if share_number_col is None:
                continue
            for tr in table.find_all("tr"):
                td = tr.find_all("td")
                if (len(td) > share_number_col):
                    text = td[share_number_col].get_text(strip=True)
                    if (text.isdigit()):
                        share_number.add(text)
        print(share_number)


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
            html_parse(report_path)
        case _:
            print(f"{file_format} cannot be parsed")
