import camelot

def pdf_parse(report_path):
    tables = camelot.read_pdf(report_path, pages='1-end', flavor='lattice', strip_text='\n', layout_kwargs={'char_margin': 0.3})

    tables = tables.stack_contiguous() 

    print(f'Number of tables found in PDF: {len(tables)}')

    for i, table in enumerate(tables):
        html_table_name = f'tables/html_table_{i}.html'
        table.to_html(html_table_name)

if __name__ == '__main__':
    pdf_parse('/mnt/c/уник/ВКР/отчет брокера Т-Банк.pdf')
