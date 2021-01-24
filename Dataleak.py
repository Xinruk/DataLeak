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

# Pool de couleur pour l'affichage
BLUE, RED, WHITE, YELLOW, MAGENTA, GREEN, END ,WARNING = '\33[94m', '\033[91m', '\33[97m', '\33[93m', '\033[1;35m', '\033[1;32m', '\033[0m', '\033[93m'

def fancyDisplay(buffer, color = WHITE):
    """
    Prend en entree un buffer et une couleur, et affiche en sortie le texte char par char
    """
    sys.stdout.write(color)
    for i in buffer:
        sys.stdout.write(i)
        sys.stdout.flush()
        time.sleep(0.02)
    sys.stdout.write(WHITE)

# Possibilite de creer des fonctions pour prendre en charge differentes API

def webCrawler(domainName, proxy_web):
    """
    Prend en entree un nom de domaine et un proxy/pool de proxies, 
    pour crawler google avec Selenium
    """

    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException

    results = {}
    
    fancyDisplay("Domain name : %s \n" % domainName)
    # Regex pour recuperer les mails d'un nom de domaine avec les sous domaines
    regex = r"[A-Za-z0-9\.\-+_]+@[A-Za-z0-9\.\-+_]*%s" % domainName
    proxy_index = 0
    PROXY = ["99.192.170.250:80", "51.75.195.37:8888", "62.171.144.29:3128"]
    
    # Pour chaque site present dans la conf, on ouvre Firefox et cherche via des GoogleDorks
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
        # l'ecriture des requetes est simulee comme un humain (certe vieux, mais humain quand meme)
        for letter in address:
            time.sleep(random.randint(0, 1))
            input_element.send_keys(letter)
        input_element.submit()
        time.sleep(2)
        print(item[0])
        mails = set()
        nextPageLink = "1"
        # Pour chaque page de recherche google, on get tous les sites
        while nextPageLink != None:
            html = driver.page_source
            new_mails = parsingGDorks(html, regex)
            if new_mails != None:
                mails.update(new_mails)
                
            try:
                # On recupere le lien de la prochaine page de recherche google
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
    """
    Prend en entree une page html et une regex, retourne les mails lies au nom de domaine
    """

    import bs4 as bs
    # Utilisation d'un set() au lieu d'un tuple/liste pour eviter les doublons
    mails = set()
    soup = bs.BeautifulSoup(pageData, "html.parser")
    links = soup.find_all("div", {"class": "yuRUbf"})
    # Pour le lien de chaque recherche google present dans la page html, on get le code source du site puis on le crawl
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
    """
    prend en entree un dictionnaire de mails pour afficher un pie plot
    """

    df = pd.DataFrame.from_dict(data=results, orient='index').transpose()
    df.to_csv('dataleak.csv') # export to csv
    df = pd.DataFrame({'Nb of leaked mail': [df.shape[0] - df['github'].isnull().sum(), df.shape[0] - df['pastebin'].isnull().sum()]},
                        index=['Github', 'Pastebin'])
    plot = df.plot.pie(y='Nb of leaked mail', figsize=(5, 5))
    plt.show()

if __name__ == '__main__':
    #Header du script
    sys.stdout.write(RED + """

 ___         _                _                _   
|   \  __ _ | |_  __ _       | |    ___  __ _ | |__
| |) |/ _` ||  _|/ _` |      | |__ / -_)/ _` || / /
|___/ \__/_| \__|\__/_|      |____|\___|\__/_||_\_\ 


""")
    Config = configparser.ConfigParser() # Config parser permet de gerer des fichiers de conf
    Config.read("config.ini")
    proxy_web = {}
    # Affiche un Warning si aucun proxy n'est set
    for item in Config.items("PROXIES"):
        if item[1] == "{}":
            fancyDisplay("Warning: no proxies are set for %s \n" % item[0], RED)

  
        
    # Argparse permet au script de prendre des parametres en entree
    parser = ArgumentParser(add_help=False)
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-h', '--help', action='help', default=SUPPRESS,
                            help='show this help message and exit')

    required.add_argument("-d", "--domainName", default = None,
                    help = "Set the domainName", required = True)

    optional.add_argument("-c", "--crawling", default = None, action = "store_true",
                    help = "Use crawling method")
    
    optional.add_argument("--api", default = None, action = "store_true",
                    help = "List set API")
    

    args = parser.parse_args()
    # Le programme change de comportement en fonction des parametres
    if args.api:
        fancyDisplay("API \n", RED)
        for item in Config.items("API"):
            fancyDisplay("%s: %s \n" % (item[0], item[1]), WHITE)

    elif args.scraping and args.domainName != None:
        webCrawler(args.domainName, proxy_web)

    else:
        parser.print_help()
