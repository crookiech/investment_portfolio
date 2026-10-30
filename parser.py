from pathlib import Path
import os
from html_parser import html_parse
from model import Report

DEFAULT_REPORT_PATH = Path("/mnt/c/уник/ВКР/отчет брокера СБЕР.HTML")
REPORT_PATH_ERROR = True

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
            # print(report)
            # usd_rate = get_current_usd_rate()
            # print(f"Dollar exchange rate: {usd_rate}")
            # print(calc_investment_portfolio_value(report, usd_rate))
            # print(calc_share_asset_in_investment_portfolio(report, usd_rate))
        case _:
            print(f"{file_format} cannot be parsed")
