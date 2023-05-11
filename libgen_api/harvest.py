#example
#download books -> analyze them -> organize in a structured format[title, authors, content, metadata, published] -> each book with all data formats => json
import os
import requests
from requests.exceptions import RequestException
import time
from libgen_api import LibgenSearch
import zipfile
from ebooklib import epub
from PyPDF2 import PdfFileReader
import json



def search_science_books(query, num_results=100):
    s = LibgenSearch()
    results = s.search_title(query)
    print(results)
    science_books = [book for book in results if "science" in book["Title"].lower()]
    print(science_books)
    return science_books[:num_results]

# books = search_science_books("science")

# download_directory = "downloads"
# os.makedirs(download_directory, exist_ok=True)

# for book in books:
#     download_links = s.resolve_download_links(book)
#     download_url = download_links.get("GET")
#     if download_url:
#         save_path = os.path.join(download_directory, f"{book['ID']}.{book['Extension']}")
#         download_book(download_url, save_path)
#         print(f"Downloaded {book['Title']} by {book['Author']} to {save_path}")

# zip_filename = "science_books.zip"

# with zipfile.ZipFile(zip_filename, 'w') as zipf:
#     for root, _, files in os.walk(download_directory):
#         for file in files:
#             file_path = os.path.join(root, file)
#             zipf.write(file_path, os.path.relpath(file_path, download_directory))



# harvestor 

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
            time.sleep(2) #wait for 2 seconds before retrying
    print(f"Failed to download {url} after {max_retries} retries.")

def extract_epub_content(file_path):
    book = epub.read_epub(file_path)
    content = []
    for item in book.get_item():
        if item.get_type() == epub.ITEM_DOCUMENT:
            content.append(item.get_content().decode('utf-8'))
    return ''.join(content)


def extract_pdf_content(file_path):
    with open(file_path, 'rb') as f:
        pdf = PdfFileReader()
        content = []
        for i in range(pdf.getNumPages()):
            content.append(pdf.getPage(i).extract_text())
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

print(extract_epub_metadata)

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

print(extract_pdf_metadata)    


def extract_metadata(file_path, extension):
    if extension == 'epub':
        return extract_epub_metadata(file_path)
    elif extension == 'pdf':
        return extract_pdf_metadata(file_path)
    else:
        return {}


s = LibgenSearch()
books = search_science_books("science")

download_directory = "downloads"
os.makedirs(download_directory, exist_ok=True)

structured_data = []
structured_data_directory = "structured_data"
os.makedirs(structured_data_directory, exist_ok=True)


for book in books:
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

        structured_data_file = os.path.join(structured_data_directory, f"{book['ID']}.json")
        with open(structured_data_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=4)

        print(f"Saved structured data for {book['Title']} by {book['Author']} to {structured_data_file}")