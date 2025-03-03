from bs4 import BeautifulSoup
import requests

import work_ids

def find_translations(search_url: str, id_limit: int | None = None):
    """
    Finds translations within the search query and matches them to their original works
    Returns a list of tuples, with the id of the translated work and the id of the original work
    """
    translation_pairs: list[tuple[int, int]] = []
    translations_found = set()
    while True:
        ids = work_ids.scrape_page(search_url)

        if not ids:
            return translation_pairs
        
        for id in ids:
            if id not in translations_found:
                original_work = get_original(id)
                if original_work:
                    translation_pairs.append((id, original_work))
                    translations_found.add(id)

                if id_limit and len(translations_found) == id_limit:
                    return translation_pairs
                
        search_url = work_ids.find_next_page(search_url)


def get_original(work_id: int):
    headers = {'User-Agent':
           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    page = requests.get(f"https://archiveofourown.org/works/{work_id}?", headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    associations = soup.select_one("ul.associations")
    if associations:
        if "A translation of" in associations.text:
            original_work = associations.select_one("a")["href"].split("/")[-1]
            return int(original_work)
    return False