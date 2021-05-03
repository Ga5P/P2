#   Importing usefull librairies :

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import re
import pandas as pd
import webbrowser

#   Knowing the browser that you will use

webbrowser.get()
result = webbrowser._tryorder
if result[1] == 'chrome':
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
if result[1] == 'firefox':
    from webdriver_manager.firefox import GeckoDriverManager
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    
#   Define the host url and the function to access content :

url = "http://books.toscrape.com/catalogue/mrs-houdini_821/index.html"
site = "http://books.toscrape.com/"

driver.get(url)
content = driver.page_source
soup = bs(content)

#   Define some usefull variabales :

wanted_info = ['product_page_url', 'upc', 'price_including_tax', 'price_excluding_tax',
            'number_available', 'title', 'category', 'review_rating',
            'image_url', 'product_description']

book_infos = {}

#-----------------------------------------------#
#   STEP ONE : GET BOOK INFO FOR ONE ELEMENT :  #
#-----------------------------------------------#

for element in soup.findAll('div',{'class': 'container-fluid page'}):
    product_page_url = url
    upc = element.findAll('td')[0].get_text()                   # We can find some wanted elements
                                                                # in 'td' tags, so we just have to
    price_including_tax = element.findAll('td')[3].text         # filter results
    price_excluding_tax = element.findAll('td')[2].text         #
    number = element.findAll('td')[5].text
    number_available = int(''.join(filter(str.isdigit, number)))
    title = element.find('h1').text
    
    c = str(element.findAll('ul', attrs={'class': 'breadcrumb'}))
    category = re.findall('\>(.*?)\<', c)[2]
    # We importing re here to avoid a two-times slicing with [start:end] just like below
    
    star = str(element.findAll('p', class_='star-rating')[0])
    start = star.find("star-rating ")+len("star-rating ")
    end = star.find('>')-1
    review_rating = star[start:end]
    # We make a slice to only get the "five" in "five stars"
    
    src = [img['src'] for img in element.findAll('img')][0]
    image_url = site + src[6:]
    # We can make a full url for the image with the end of the "src" and the site's url
    
    d = str(soup.findAll('meta', attrs={'name': 'description'}))
    product_description = re.findall(r'\"([^"]*)\"', d)[0].replace('\n', '')
    
    infos = [product_page_url, upc, price_including_tax, price_excluding_tax,
            number_available, title, category, review_rating, image_url,
            product_description]
    # We making a list with all our recovered infos
    
    book_info = {inf: var for inf,var in zip(wanted_info, infos)}
    # We stock the result in a dictionnary to keep the association {wanted_info : info}
    # from our two lists
    
    book_infos[title] = book_info   # We can save all informations of this specific book
                                    # in a new dictionnary
                                    
# Then we can tranform it into DataFrame with our wanted infos as columns     
df = pd.DataFrame.from_dict(book_infos, orient='index')
# And save it in csv format
df.to_csv('Mrs_Houdini.csv')