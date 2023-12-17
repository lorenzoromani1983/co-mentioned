import requests
import unidecode
import itertools
import re
import os
import csv
from inscriptis import get_text
from multiprocessing import Pool, Manager
import numpy as np
from functools import partial

def search(combination, urls, token):
    print("Searching: ", combination)
    response = requests.get(
        "https://api.scaleserp.com/search",
        params={"api_key": token, "q": '"' + combination[0] + '"' + " " + '"' + combination[1] + '"', "num":100},
    ).json()
    if "organic_results" in response:
        for row in response["organic_results"]:
            if "link" in row and "snippet" in row:
                link = row["link"]
                urls.append(link)
    else:
        print("[!] No results available or query limit reached")

def check_remaining_requests(token):
    response = requests.get("https://api.scaleserp.com/account", params={"api_key": token}).json()
    remaining_requests = response["account_info"]["credits_remaining"]
    return remaining_requests

def check_url(url, pattern, done):
    attempts = 0
    while attempts < 4:
        try:
            corpus = get_text(requests.get(url, timeout=20).text)
        except Exception as e:
            print(f"Error on url {url}, :{e}")
            attempts += 1
            continue
        body = unidecode.unidecode(corpus).lower()
        results = pattern.findall(body)
        indexes_list = list()
        if len(set(results)) > 1:
            tokens = list()
            for entity in set(results):
                token = "_".join(entity.split())
                tokens.append(token)
                new_body = re.sub(entity, token, body)
                body = new_body
            without_punctuation = re.sub("[^0-9a-zA-Z&@_+]+", " ", body)
            single_spaced_text = re.sub("\s+", " ", without_punctuation).strip()
            text_to_list = single_spaced_text.split()
            for token in tokens:
                entity_indexes = [
                    index for index, value in enumerate(text_to_list) if value == token
                ]
                indexes_list.append(entity_indexes)
            all_diffs = list()
            products = list(itertools.product(*indexes_list))
            for distance_eval in products:
                combinations = itertools.combinations(distance_eval, 2)
                for combination in combinations:
                    diff = min(abs(np.diff(combination)), default=0)
                    all_diffs.append(diff)
            minimum_diff = min(all_diffs, default=0)
            evaluated_source = {'url': url, 'entities': set(results), 'distance': minimum_diff}
            done.append(evaluated_source)
            print(minimum_diff, " >>> ", set(results), " >>> ", url)
            break

        if len(set(results)) <= 1:
            break
        
        if attempts == 4:
            break

def main():
    
    manager = Manager()
    evaluated = manager.list()
    path = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(path, "REPORT"+".csv")        
    
    targets = [
        unidecode.unidecode(target.rstrip("\n").lower())
        for target in open(os.path.join(path, "entities.txt")).readlines()
    ]

    token_ = [
        key.rstrip("\n")
        for key in open(os.path.join(path, "token.txt")).readlines()
    ]
    
    token = token_[0]
    
    credits_available = check_remaining_requests(token)
    
    pattern = re.compile("|".join(targets))
    combos = list(itertools.combinations(targets, 2))
    
    if len(combos) <= credits_available:
        
        print(f"{credits_available} ScaleSerp requests left")
    
        print("Iterating over " + str(len(combos)) + " combinations\n")
    
        print("Search started\n")
    
        manager = Manager()
        links = manager.list()
        kwargs = {"urls": links, 'token': token}
        p = Pool(os.cpu_count())
        mapfunc = partial(search, **kwargs)
        p.map(mapfunc, combos)
        p.close()
        p.join()
        
        print("\nSearch finished\n")
        
        print("Investigating "+ str(len(set(links)))+" sources\n")
    
        manager = Manager()
        kwargs = {"pattern": pattern, "done": evaluated}
        p = Pool(os.cpu_count())    
        mapfunc = partial(check_url, **kwargs)
        p.map(mapfunc, set(links))
        p.close()
        p.join()
        
        with open(file,'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter ="|" )
            header = ['URL','Entities','Distance']
            writer.writerow(header)
            for source in evaluated:
                rows = [source['url'], source['entities'], source['distance']]
                writer.writerow(rows)
                
        print("\nResults saved in "+file)
    
    else:
        print("Credits limit reached. Replace your ScaleSerp token")
    
if __name__ == "__main__":
    main()
    

    
  
