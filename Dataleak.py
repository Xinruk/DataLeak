import requests
import configparser
import time
from argparse import ArgumentParser, SUPPRESS
import sys

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
        # if item[0] != "pastebin" and item[1] != "KEY":
        #     requests.get("https://scrape.pastebin.com/api_scrape_item.php?i=@domainName")
        pass
        

def webCrawler(domainName):
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select

    results = {}
    fancyDisplay("Domain name : %s \n" % domainName)
    # regex = "^[_A-Za-z0-9-\\+]+(\\.[_A-Za-z0-9-]+)*@%s$" % domainName
    # regex = "^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?(domain|domain2)\.com$" 
    regex = r"[A-Za-z0-9\.\-+_]+@%s" % domainName

    driver = webdriver.Firefox()
    for item in Config.items("SITE"):
        driver.get("https://www.google.com")
        input_element = driver.find_element_by_name("q")
        input_element.send_keys("site:%s intext:@%s" % (item[1], domainName))
        input_element.submit()
        time.sleep(2)
        
        html = driver.page_source
        print(item[0])
        ## Faire comme bs4 avec selenium . l'idee est de passer a parsingGDorks un tableau de page
        # nextPageLink = soup.find("a", id="pnnext").get("href").click()
        mails = parsingGDorks(html, regex)
        results.update({item[0]:mails})        
        


        
def parsingGDorks(pageData, regex):
    import bs4 as bs
    import re
    mails = set()
    ## Mettre ne place un for page in page Array
    # nextPageLink = "1"
    # while nextPageLink != None:
    soup = bs.BeautifulSoup(pageData, "html.parser")
    links = soup.find_all("div", {"class": "yuRUbf"})
    for link in links:
        url = link.find("a").get("href")
        linkData = requests.get(url)
        linkData = linkData.text
        new_mails = set(re.findall(regex, linkData))
        mails.update(new_mails)
    if mails != set():
        print(mails)
        return mails
    else:
        print("None")
        return None
        # nextPageLink = soup.find("a", id="pnnext").get("href")
        # pageData = requests.get(nextPageLink).text

    

    

if __name__ == '__main__':
    sys.stdout.write(RED + """

 ___         _                _                _   
|   \  __ _ | |_  __ _       | |    ___  __ _ | |__
| |) |/ _` ||  _|/ _` |      | |__ / -_)/ _` || / /
|___/ \__/_| \__|\__/_|      |____|\___|\__/_||_\_\ 


""")
    Config = configparser.ConfigParser()
    Config.read("config.ini")


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
        webCrawler(args.domainName)

    
    else:
        parser.print_help()

