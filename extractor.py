### This file contains functions used to extract data from a given ebay product URL
### Use scheduler.py to run this script through a list of URLs

import re # regex
import requests # HTTP requests
from bs4 import BeautifulSoup

from util import trimUrlArguments # HTML DOM parser

def parse_price(price_string):
    match = re.match(r'(?P<pre>\D*)(?P<price>\d+([,\.]\d+)?)(?P<post>\D*?)$', price_string)

    if not match:
        return price_string
    
    pre = match.group('pre').strip()
    value = match.group('price').strip()
    post = match.group('post').strip()

    is_usd = pre == "US $" or pre.strip() == "USD"

    return (pre if not is_usd else "") + value.replace(",", "").replace(".", ",") + (post if post != "/ea" else "")

def get_options_prices(soup):
    raw = [script.text for script in soup.select("script")
        if (("variationsMap" in script.text) and ("binModel" in script.text))]

    option_names = [""]
    
    if not raw:
        raw = [script.text for script in soup.select("script") if "binModel" in script.text]

        if not raw:
            # read the price from the page itself
            price_string = soup.select_one(".x-price-primary span").text
            return [("", parse_price(price_string))]

        raw = raw[0]
    else:
        raw = raw[0]
        
        # Get option names
        scope = re.search(r'(?<=menuItemMap).+?(?=variationsMap)', raw).group()
        option_names = [match.group() for match in re.finditer(r'(?<="displayName":").+?(?=")', scope)]

    # Get prices
    prices = []
    for option_raw in raw.split("binModel")[1:]:
        # print(option_raw)
        
        price = re.search(r'(?<="convertedFromValue":).+?(?=,)', option_raw)
        currency = re.search(r'(?<="convertedFromCurrency":").+?(?=")', option_raw)

        if price == None:
            price = re.search(r'(?<="value":)[\d,\.]+?(?=,)', option_raw)
            currency = re.search(r'(?<="currency":").+?(?=")', option_raw)

        prices.append(parse_price(f"{currency.group()} {price.group()}") if price else "")

    return list(zip(option_names, prices))

def get_shipping(soup):
    shipping_string = soup.select_one('.ux-labels-values--shipping .ux-textspans--BOLD').text

    if "free" in shipping_string.lower() or "ingyenes" in shipping_string.lower():
        return "0"
    
    if "does not ship" in shipping_string.lower() or "nem szállít" in shipping_string.lower():
        return "x"

    return parse_price(shipping_string)

def format_date(date_string):
    match = re.search(r'.+, (?P<month>\w+) (?P<day>\d+)', date_string)

    if not match:
        match = re.search(r'(?P<month>\w+)\. (?P<day>\d+)\.', date_string)
    
    month = match.group('month').strip().lower()
    day = match.group('day').strip()
    return f"{month} {day}"

def get_delivery_date(soup):
    delivery = soup.select('.ux-labels-values--deliverto .ux-textspans--BOLD')

    if not delivery:
        return ""
    
    delivery_min = delivery[0].text
    delivery_max = delivery[1].text
    
    return f"{format_date(delivery_min)}–{format_date(delivery_max)}"

def get_descriptions(soup, options_count):
    src = soup.select_one("#desc_ifr")["src"]
    iframe_content = requests.get(src).content
    iframe_soup = BeautifulSoup(iframe_content, "html.parser")

    text = iframe_soup.get_text().lower()
    
    delimiter = next((delimiter for delimiter in ["package include", "package list", "included in"] if delimiter in text), None)
    if not delimiter:
        return [""] * options_count # return empty descriptions

    contents = text.split(delimiter, 1)[1]

    def get_item_count(item_names):
        if not isinstance(item_names, list):
            item_names = [item_names]

        item_names = [item.lower() for item in item_names]
        
        # format: 1 x item_name
        count = max([len(re.findall(rf'^1 ?[x×] ?{item}', contents)) for item in item_names])
        if count > 0:
            return count
        
        # format: 1* item_name
        count = max([len(re.findall(rf'^1 ?\* ?{item}', contents)) for item in item_names])
        if count > 0:
            return count
        
        # format: item_name (without other text in the line)
        count = max([len(re.findall(rf'^{item}\W*$', contents, re.MULTILINE)) for item in item_names])
        if count > 0:
            return count

        # format: item_name (anywhere in text)
        count = max([contents.count(item) for item in item_names])
        return count

    safety_switch = get_item_count("safety switch")
    buzzer = get_item_count("buzzer")
    ppm_decoder = get_item_count(["ppm decoder", "ppm encoder", "ppm module"])
    micro_sd = get_item_count(["microsd", "micro sd", "sd card"])
    iic_board = get_item_count(["i2c board", "i2c expansion", "i2c module"])
    gps = get_item_count(["m8n gps", "gps module"])
    power_module = get_item_count(["power module", "current meter"])
    shock_absorber = get_item_count(["shock absorber", "shocker absorber"])

    flight_controller = ("TRUE"
        if (
        (safety_switch > 0)
        + (buzzer > 0)
        + (ppm_decoder > 0)
        + (micro_sd > 0)
        + (iic_board > 0)
        + (gps > 0)
        + (power_module > 0)
        ) >= 2
        else "")

    descriptions = []
    for i in range(0, options_count):
        def check_quantity(quantity):
            if quantity > options_count:
                return "?"

            return "TRUE" if quantity >= (options_count - i) else ""

        description = f"{flight_controller}\t{check_quantity(gps)}\t{check_quantity(power_module)}\t{check_quantity(iic_board)}\t{check_quantity(ppm_decoder)}\t{check_quantity(buzzer)}\t{check_quantity(safety_switch)}\t\t\t{check_quantity(micro_sd)}\t{check_quantity(shock_absorber)}"
        descriptions.append(description)

    return descriptions

def get_summary(url, parse_contents = True):
    url_without_query_string = trimUrlArguments(url)
    url_with_language = url_without_query_string + "?_language=en-US"
    
    response = requests.get(url_with_language)
    content = response.content

    ended = [
        "This listing has ended.",
        "Ez a listázás véget ért",
        "bidding has ended",
        "licitálás befejeződött",
    ]

    if any((x.lower() in content.decode("utf-8").lower()) for x in ended):
        return [f"\t{url_without_query_string}\t\texpired"]
        
    soup = BeautifulSoup(content, 'html.parser')

    options_prices = get_options_prices(soup)
    options_count = len(options_prices)
    shipping = get_shipping(soup)
    delivery_date = get_delivery_date(soup)
    
    descriptions = get_descriptions(soup, options_count)

    summaries = []
    for i in range(0, options_count):
        option_name = options_prices[i][0]
        price = options_prices[i][1]
        description = descriptions[i]
        
        summary = f"\t\t{url_without_query_string}\t{option_name}\t{price}\t\t{shipping}\t\t\t\t{delivery_date}"
        if parse_contents:
            summary = f"{summary}\t{description}"

        summaries.append(summary)

    return summaries
