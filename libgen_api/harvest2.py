import os
import requests
from requests.exceptions import RequestException
import time
from libgen_api import LibgenSearch
import zipfile
import threading
from ebooklib import epub
from PyPDF2 import PdfReader
# from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import json
import gzip


def search_science_books(query, num_results=100):
    s = LibgenSearch()
    results = s.search_title(query)
    science_books = [book for book in results if "science" in book["Title"].lower()]
    return science_books[:num_results]


def download_book(url, save_path, max_retries=3, timeout=10):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return
        except RequestException:
            print(f"Download failed, retrying {retries + 1}/{max_retries}")
            retries += 1
            time.sleep(2)
    print(f"Failed to download {url} after {max_retries} retries.")


def extract_epub_content(file_path):
    book = epub.read_epub(file_path)
    content = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            content.append(BeautifulSoup(item.get_content(), 'html.parser').get_text())
    return '\n'.join(content)

def extract_pdf_content(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfReader(f)
        content = []
        for i in range(len(pdf.pages)):
            content.append(pdf.pages[i].extract_text())
    return ''.join(content)


def extract_epub_metadata(file_path):
    book = epub.read_epub(file_path)
    return {
        'title': book.get_metadata('DC', 'title')[0][0],
        'authors': [author[0] for author in book.get_metadata('DC', 'creator')],
        'language': book.get_metadata('DC', 'language')[0][0],
        'publisher': book.get_metadata('DC', 'publisher')[0][0] if book.get_metadata('DC', 'publisher') else '',
        'published': book.get_metadata('DC', 'date')[0][0] if book.get_metadata('DC', 'date') else '',
        'content': extract_epub_content(file_path),
    }


def extract_pdf_metadata(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        return {
            'title': info.title,
            'authors': [info.author] if info.author else [],
            'language': '',
            'publisher': info.producer if info.producer else '',
            'published': info.creationDate if info.creationDate else '',
            'content': extract_pdf_content(file_path),
        }


def extract_metadata(file_path, extension):
    if extension == 'epub':
        return extract_epub_metadata(file_path)
    elif extension == 'pdf':
        return extract_pdf_metadata(file_path)
    else:
        return {}


def save_structured_data(structured_data, file_path):
    with gzip.open(file_path, 'wt', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)


def process_book(book, download_directory, structured_data_directory):
    s = LibgenSearch()
    download_links = s.resolve_download_links(book)
    download_url = download_links.get("GET")
    if download_url:
        save_path = os.path.join(download_directory, f"{book['ID']}.{book['Extension']}")
        download_book(download_url, save_path)
        print(f"Downloaded {book['Title']} by {book['Author']} to {save_path}")
        metadata = extract_metadata(save_path, book["Extension"])

        structured_data = {
            "ID": book["ID"],
            "Title": book["Title"],
            "Authors": book["Author"].split(', '),
            "Publisher": book["Publisher"],
            "Year": book["Year"],
            "Pages": book["Pages"],
            "Language": book["Language"],
            "Size": book["Size"],
            "Extension": book["Extension"],
            **metadata
        }
        print(structured_data)

        structured_data_file = os.path.join(structured_data_directory, f"{book['ID']}.json.gz")
        save_structured_data(structured_data, structured_data_file)

        print(f"Saved structured data for {book['Title']} by {book['Author']} to {structured_data_file}")


s = LibgenSearch()
books = search_science_books("science", num_results=10)

download_directory = "downloads"
os.makedirs(download_directory, exist_ok=True)

structured_data_directory = "structured_data"
os.makedirs(structured_data_directory, exist_ok=True)

# Use threading to speed up the downloading and processing of books
threads = []

for book in books:
    thread = threading.Thread(target=process_book, args=(book, download_directory, structured_data_directory))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("Finished processing all books.")
