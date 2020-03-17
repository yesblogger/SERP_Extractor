from requests import Session
from urllib.parse import urlparse, parse_qs, urlsplit
from fake_useragent import UserAgent
from lxml import html
import pandas as pd
import csv


# instance to create a fake user agent
UA = UserAgent()

# Dataset to capture the scraped data.
dataset = []


def get_cookie():
    """[fetches the cookie from a file]

    Returns:
        [string] -- [cookie for authentication]
    """
    with open("cookie.txt", mode="r") as r_file:
        return r_file.readline()


def url_parse(keyword):
    output = keyword.split()
    if len(output) > 1:
        return output[0]
    else:
        return "%20".join(output)


def url_extract(href):
    return parse_qs(urlparse(href).query)['q']


def get(item):
    try:
        return item.pop(0)
    except:
        return ""


def extractor():
    """Main function to execute the data extraction process
    """
    # creating a requests Session instance
    session = Session()
    session.headers.update({
        'user-agent': UA.chrome,
        'cookie': get_cookie()
    })
    # fetching the authentication token
    p_resp = html.fromstring(session.get("https://www.google.com").text)
    sxsrf = p_resp.xpath("//input[@name='sxsrf']/@value")
    ei = p_resp.xpath("//input[@name='ei']/@value")
    ved = p_resp.xpath("//input[@name='q']/@data-ved")
    # updating session with new header information
    session.headers.update({
        "referer": "https://www.google.com/"
    })
    # fetching the inputs from the user
    keyword = url_parse(input("please enter the keyword: "))
    # creating the query string parameter
    query = {

        "safe": "active",
        "hl": "en",
        "sxsrf": sxsrf,
        "source": "hp",
        "ei": ei,
        "q": keyword,
        "oq": keyword,
        "ved": ved,
        "uact": 5
    }
    # making the get request to google.
    resp = session.get("https://www.google.com/search?", params=query).text
    # parsing the html content of the page
    parsed_content = html.fromstring(resp)
    # setting the counter for the index
    index_counter = 1
    for item in parsed_content.xpath('//a[div[@class="TbwUpd NJjxre"]]'):
        url_raw = get(item.xpath('./@href'))
        title = get(item.xpath('./h3/text()')).strip()
        #url = get(url_extract(url_raw))
        domain = urlsplit(url_raw)[1]
        dataset.append({
            'Est Rank': index_counter,
            'Page Title': title,
            'Domain': domain,
            'URL': url_raw
        })
        index_counter += 1


def write_to_csv():
    with open("serp.csv", mode="w", newline="", encoding="utf-8") as w_file:
        # creating header of the new csv file
        header = ['Est Rank', 'Page Title', 'Domain', 'URL']
        # setting csv instance with the header
        writer = csv.DictWriter(w_file, fieldnames=header)
        writer.writeheader()
        for i in dataset:
            writer.writerow(i)


def output_logic():
    resp = input("You want the output in a csv file (Yes or No): ").upper()
    if resp == "YES" and len(dataset):
        write_to_csv()
    else:
        print(pd.DataFrame(dataset))


if __name__ == "__main__":
    extractor()
    output_logic()
