### This script is used to schedule the extractor.py script to run through a list of URLs

from pyperclip import copy
from os import system
import sys

from extractor import get_summary
from util import clearConsole, trimUrlArguments

command_line_args = sys.argv[1:]

if "-h" in command_line_args or "--help" in command_line_args:
    print("Command line arguments:")
    print("-h, --help:\t\tShow this help message")
    print("-d, --dont-clear:\tDon't clear the console before running")
    print("-v, --verbose:\t\tNotify while running when a URL failed to be parsed")
    print("\tIf this argument is not specified, the failed URLs are first retried" +
          "\n\tand if the retries fail, they will be displayed only at the end of the run")
    
    sys.exit()

if "-d" not in command_line_args and "--dont-clear" not in command_line_args:
    clearConsole()

urls = [
    "https://www.ebay.com/itm/201723332948",
    "https://www.ebay.com/itm/204355711714",
    "https://www.ebay.com/itm/123772651468",
    "https://www.ebay.com/itm/125403536735",
    "https://www.ebay.com/itm/154627344701",
    "https://www.ebay.com/itm/154660911645",
    "https://www.ebay.com/itm/165386772432",
    "https://www.ebay.com/itm/165489612954",
    "https://www.ebay.com/itm/255436257992",
    "https://www.ebay.com/itm/255616205778",
    "https://www.ebay.com/itm/274724049454",
    "https://www.ebay.com/itm/284466362618",
    "https://www.ebay.com/itm/295001465675",
    "https://www.ebay.com/itm/401598943536",
    "https://www.ebay.com/itm/401598945073",
    "https://www.ebay.com/itm/402704631715",
    "https://www.ebay.com/itm/152836486311",
    "https://www.ebay.com/itm/255055738101",
    "https://www.ebay.com/itm/256147868144",
    "https://www.ebay.com/itm/275244037371",
    "https://www.ebay.com/itm/354834215723",
    "https://www.ebay.com/itm/175739246655",
    "https://www.ebay.com/itm/202060669242",
    "https://www.ebay.com/itm/311852214732",
    "https://www.ebay.com/itm/314076540299",
    "https://www.ebay.com/itm/314076540299",
    "https://www.ebay.com/itm/125094437332",
    "https://www.ebay.com/itm/125249976612",
    "https://www.ebay.com/itm/125282686948",
    "https://www.ebay.com/itm/125282688385",
    "https://www.ebay.com/itm/155463945805",
    "https://www.ebay.com/itm/155463945805",
    "https://www.ebay.com/itm/165458160410",
    "https://www.ebay.com/itm/165467595797",
    "https://www.ebay.com/itm/165467595797",
    "https://www.ebay.com/itm/165467595797",
    "https://www.ebay.com/itm/165467595797",
    "https://www.ebay.com/itm/173981292247",
    "https://www.ebay.com/itm/173981292247",
    "https://www.ebay.com/itm/175328606075",
    "https://www.ebay.com/itm/175429824406",
    "https://www.ebay.com/itm/175429824406",
    "https://www.ebay.com/itm/175430717105",
    "https://www.ebay.com/itm/175805311641",
    "https://www.ebay.com/itm/175832523070",
    "https://www.ebay.com/itm/185487611972",
    "https://www.ebay.com/itm/254951373789",
    "https://www.ebay.com/itm/265154870750",
    "https://www.ebay.com/itm/266362701794",
    "https://www.ebay.com/itm/275981481942",
    "https://www.ebay.com/itm/284732189871",
    "https://www.ebay.com/itm/284789595740",
    "https://www.ebay.com/itm/284937098682",
    "https://www.ebay.com/itm/285356752268",
    "https://www.ebay.com/itm/285401626883",
    "https://www.ebay.com/itm/354229052638",
    "https://www.ebay.com/itm/384413634574",
    "https://www.ebay.com/itm/384413634574",
    "https://www.ebay.com/itm/384413634574",
    "https://www.ebay.com/itm/384413634574",
    "https://www.ebay.com/itm/385405633800",
    "https://www.ebay.com/itm/404175469472",
    "https://www.ebay.com/itm/404386425612",
    "https://www.ebay.com/itm/182717071164",
    "https://www.ebay.com/itm/264845165976",
    "https://www.ebay.com/itm/265166221718",
]

urls = [url for url in urls if url != ""] # remove empty urls
original_urls_count = len(urls)
urls = [trimUrlArguments(url) for url in urls] # remove arguments from urls
urls = list(set(urls)) # remove duplicates

if (len(urls) != original_urls_count):
    print(f"Removed {original_urls_count - len(urls)} duplicate URLs, {len(urls)} unique URLs remain.")

# get the summaries and aggregate them
print("Starting...")

summaries = []
for i in range(0, 3):
    failed_urls = []

    for url in urls:
        summary = []

        try:
            summary = get_summary(url)
            summaries.extend(summary)
            for s in summary:
                print(s)
            
        except Exception as err:
            failed_urls.append(url)
        #     print(f"Error downloading {url}:\n\t{err}")
    
    if len(failed_urls) == 0:
        break

    urls = failed_urls

if len(failed_urls) > 0:
    print(f"Failed to download {len(failed_urls)} urls:")
    for url in failed_urls:
        print(f"\t{url}")
else:
    print("All urls downloaded successfully.")

summaries_string = '\n'.join(summaries)

# print(summaries_string)

# copy the results to the clipboard
copy(summaries_string)
