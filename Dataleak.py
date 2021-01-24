import re
from bs4.element import PreformattedString
import requests
import configparser
import time
from argparse import ArgumentParser, SUPPRESS
import sys
import pandas as pd
import random
import matplotlib.pyplot as plt

BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END ,WARNING = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m', '\033[93m'

def fancyDisplay(buffer, color = WHITE):
    sys.stdout.write(color)
    for i in buffer:
        sys.stdout.write(i)
        sys.stdout.flush()
        time.sleep(0.02)
    sys.stdout.write(WHITE)

def webScraper(domainName):
    fancyDisplay("Domain name : %s" % domainName)
    for item in Config.items("API"):
        pass
        

def webCrawler(domainName, proxy_web):
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException

    results = {}
    
    fancyDisplay("Domain name : %s \n" % domainName)

    regex = r"[A-Za-z0-9\.\-+_]+@[A-Za-z0-9\.\-+_]*%s" % domainName
    proxy_index = 0
    PROXY = ["99.192.170.250:80", "51.75.195.37:8888", "62.171.144.29:3128"]
    # 

    for item in Config.items("SITE"):
        webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
        "httpProxy": PROXY[proxy_index],
        "ftpProxy": PROXY[proxy_index],
        "sslProxy": PROXY[proxy_index],
        "proxyType": "MANUAL",
        }
        driver = webdriver.Firefox()
        driver.get("https://www.google.com")
        input_element = driver.find_element_by_name("q")
        address = "site:%s intext:@%s" % (item[1], domainName)
        for letter in address:
            time.sleep(random.randint(0, 1))
            input_element.send_keys(letter)
        input_element.submit()
        time.sleep(2)
        print(item[0])
        mails = set()
        nextPageLink = "1"
        while nextPageLink != None:
            html = driver.page_source
            new_mails = parsingGDorks(html, regex)
            if new_mails != None:
                mails.update(new_mails)
                
            try:
                nextPageLink = driver.find_element_by_xpath("//*[@id='pnnext']").get_attribute("href")
                time.sleep(40)
                driver.get(nextPageLink)
            except NoSuchElementException:
                nextPageLink = None
        results.update({item[0]:mails})
        if proxy_index < 3 :
            proxy_index += 1
        else:
            proxy_index = 0
        driver.close()
    dataVisu(results)
        
        
def parsingGDorks(pageData, regex):
    import bs4 as bs
    mails = set()
    soup = bs.BeautifulSoup(pageData, "html.parser")
    links = soup.find_all("div", {"class": "yuRUbf"})
    for link in links:
        url = link.find("a").get("href")
        linkData = requests.get(url)
        linkData = linkData.text
        new_mails = set(re.findall(regex, linkData))
        mails.update(new_mails)
    if mails != set():
        return mails
    else:
        return None
    
def dataVisu(results):
    df = pd.DataFrame.from_dict(data=results, orient='index').transpose()
    df.to_csv('dataleak.csv') # export to csv
    df = pd.DataFrame({'Nb of leaked mail': [df.shape[0] - df['github'].isnull().sum(), df.shape[0] - df['pastebin'].isnull().sum()]},
    index=['Github', 'Pastebin'])
    plot = df.plot.pie(y='Nb of leaked mail', figsize=(5, 5))
    plt.show()

if __name__ == '__main__':
    sys.stdout.write(RED + """

 ___         _                _                _   
|   \  __ _ | |_  __ _       | |    ___  __ _ | |__
| |) |/ _` ||  _|/ _` |      | |__ / -_)/ _` || / /
|___/ \__/_| \__|\__/_|      |____|\___|\__/_||_\_\ 


""")
    Config = configparser.ConfigParser()
    Config.read("config.ini")
    proxy_web = {}
    for item in Config.items("PROXIES"):
        if item[1] == "{}":
            fancyDisplay("Warning: no proxies are set for %s \n" % item[0], RED)
        # if item[0] == "web":
        #     proxy_web = item[1]
  
        

    parser = ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-h', '--help', action='help', default=SUPPRESS,
                            help='show this help message and exit')

    required.add_argument("-d", "--domainName", default = None,
                    help = "Set the domainName", required = True)

    optional.add_argument("-p", "--parsing", default = None, action = "store_true",
                    help = "Use parsing method")

    optional.add_argument("-s", "--scraping", default = None, action = "store_true",
                    help = "Use scrapping method")
    
            
    optional.add_argument("--api", default = None, action = "store_true",
                    help = "List set API")
    

    args = parser.parse_args()

    if args.api:
        fancyDisplay("API \n", RED)
        for item in Config.items("API"):
            fancyDisplay("%s: %s \n" % (item[0], item[1]), WHITE)

    elif args.parsing and args.domainName != None:
        webScraper(args.domainName)

    elif args.scraping and args.domainName != None:
        webCrawler(args.domainName, proxy_web)

    
    else:
        parser.print_help()
