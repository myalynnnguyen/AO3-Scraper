from collections import defaultdict
import argparse
from multiprocessing import Process, Manager, Lock

import requests
from bs4 import BeautifulSoup

import work_ids

PROCESS_COUNT = 8
def main():
    search_url = ""
    id_limit = None
    n = 1
    exclude_count = False
    exclude_lower = 0

    parser = argparse.ArgumentParser()
    parser.add_argument('search_url', help="url of search query")
    parser.add_argument('--id_limit', type=int, required=False, 
                        help="limit of work id's to retrieve, defaults to no limit")
    parser.add_argument('--n', type=int, required=False, 
                        help="max n-gram length to record, defaults to 1")
    parser.add_argument('--exclude_count', action='store_true', 
                        help="exclude occurence count of ngrams from output")
    parser.add_argument('--exclude_lower', type=int, required=False, 
                        help="exclude ngrams with less than X occurences")
    args = parser.parse_args()
    if args.search_url:
        search_url = args.search_url
    if args.id_limit:
        id_limit = args.id_limit
    if args.n:
        n = args.n
    if args.exclude_count:
        exclude_count = True
    if args.exclude_lower:
        exclude_lower = args.exclude_lower

    ngrams = defaultdict(int)
    ids = list(work_ids.scrape(search_url, id_limit))
    split_ids = [ids[(i*len(ids)) // PROCESS_COUNT : 
                ((i+1)*len(ids)) // PROCESS_COUNT] for i in range(PROCESS_COUNT)]

    manager = Manager()
    lock = Lock()
    ngrams = manager.dict()

    processes: list[Process] = []
    for process in range(PROCESS_COUNT):
        processes.append(Process(target=parse_page_multiprocess,
                                 args=[split_ids[process], n, ngrams, lock]))
        processes[process].start()
    for process in range(PROCESS_COUNT):
        processes[process].join()
        
    for ngram, count in sorted(ngrams.items(), key=lambda x: x[1], reverse=True):
        if count < exclude_lower:
            break

        if not exclude_count:
            print(ngram, count)
        else:
            print(ngram)

def parse_page(work_id: int, n: int) -> dict[str, int]:
    """
    Parses work and returns dict of ngram to ngram occurence count
    """
    ngrams = defaultdict(int)
    current_ngram = []
    url = f"https://archiveofourown.org/works/{work_id}?view_full_work=true"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    blocks = soup.select("#work")
    for block in blocks:
        #discarding ao3 "Chapter/Work Text" header
        content = block.parent.text.split("Text", 1)[1]
        #removing punctuation
        for p in "/!\"#$%&()*+,-./:;<=>?@[\]^_`{|}~\'…“”‘’」「—":
            content = content.replace(p, " ")

        words = content.split()
        for word in words:
            word = word.strip().lower()
            current_ngram.append(word)

            if len(current_ngram) > n:
                current_ngram.pop(0)

            for i in range(len(current_ngram)):
                ngram = ""
                for j in range(i + 1):
                    ngram += current_ngram[j] + " "
                ngram = ngram[:-1]
                ngrams[ngram] += 1
    
    return ngrams

def parse_page_multiprocess(ids: list[int], n:int, ngrams:dict, lock):
    for id in ids:
        try:
            ret = parse_page(id, n)
            with lock:
                for x, y in ret.items():
                    if x in ngrams:
                        ngrams[x] += y
                    else:
                        ngrams[x] = y
        except Exception as e:
            print(f"An error occured with work id {id}")
            print(e)

if __name__ == '__main__':
    main()