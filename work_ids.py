from typing import Callable

import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry

def scrape(search_url: str, id_limit: int | None = None):
    """
    Given url of a search, returns all work id's from all pages
    Work id's will be given as an argument to the condition function (if given)
    Work id will only be collected if condition returns true
    """
    work_ids = []
    while True:
        ids = scrape_page(search_url)

        if not ids:
            return work_ids
        
        for id in ids:
            if id not in work_ids:

                work_ids.append(id)

                if id_limit and len(work_ids) == id_limit:
                    return work_ids
                
        search_url = find_next_page(search_url)

#limiting rate to 50 requests every 5 seconds
@sleep_and_retry
@limits(calls=50, period=5)
def scrape_page(page_url: str) -> list[int]:
    """
    Returns all the work_ids on one page
    """
    headers = {'User-Agent':
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    page = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    works = soup.select("li.work.blurb.group")
    work_ids = []
    for work in works:
            id = work["id"][len("work_"):]
            work_ids.append(int(id))
    return work_ids

def find_next_page(url: str):
    """
    Next page of search results
    """
    if "page=" in url:
        page_number_index = url.find("page=") + len("page=")
        page_number = "" 
        while page_number_index < len(url) and url[page_number_index].isdigit():
            page_number += url[page_number_index]
            page_number_index+=1
        page_number = int(page_number)

        updated_page = f"page={page_number + 1}"
        if page_number_index < len(url) and url[page_number_index] != '&':
            updated_page += "&"

        return url.replace(f"page={page_number}", updated_page)
    
    if "archiveofourown.org/works" in url:
        url.find("search?")
        return url.replace("search?", "search?commit=Search&page=2&")
        
    if "archiveofourown.org/tags" in url:
        return url[:url.find("/works")] + "/works?page=2&"
