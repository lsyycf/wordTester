import os
import re
import fitz


def read_pdf(book_path):
    if not os.path.exists(book_path):
        return None
    document = fitz.open(book_path)
    text = ''
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        page_text = page.get_text("text")
        pattern = r'(?<!。)\n'
        page_text = re.sub(pattern, '', page_text)
        text = text + page_text
    text = text.replace('\n', '\n  ')
    document.close()
    return text
