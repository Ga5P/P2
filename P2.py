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
    
#   Define the host url :

site = "http://books.toscrape.com/"

#   Define a function to access content that retruns soup, 
#   that avoids some repetitions in the code :

def read_url(url):
    driver.get(url)
    content = driver.page_source
    soup = bs(content)
    return soup

#   Define some usefull variabales :

wanted_info = ['product_page_url', 'upc', 'price_including_tax', 'price_excluding_tax',
            'number_available', 'title', 'category', 'review_rating',
            'image_url', 'product_description']

#------------------------------------------------------#
#   STEP TWO : GET BOOK INFO FOR AN ENTIRE CATEGORY :  #
#------------------------------------------------------#

#   Making an empty list to store all urls of the books in a category :
all_url = []

#   Let's take a category with several pages of results, like Non Fiction :
cat_url = 'http://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'

# We'll need this piece of url wich is present in the product page
slice_1 = "catalogue/"

# The site's structure allows to replace "index.html" at the first page to "page-1.html"
# we can make a slice by removing the end
slice_2 = cat_url[:-len("index.html")-1]

#   Getting the number of pages...
page_number = int(read_url(cat_url).find('li',{'class': 'current'})
                          .text.replace(" ","").replace("\n",'')[-1])

#   and the number of results
nb_result = int(read_url(cat_url).findAll('strong')[1].get_text())

#   We have 20 results by page, so :
if nb_result > 20:
            
            # The range goes from page 1 to page 6
            list_pages = range(1, page_number+1)
            # A generator with a format string allows to have all end of urls in our category
            list_pages = [f"/page-{p}.html" for p in list_pages]
            # And another one to get all entires urls for the category results
            pages_url = [f'{slice_2}{p}' for p in list_pages]


for url in pages_url:
            
            for i in read_url(url).find_all('article',{'class': 'product_pod'}):
                # Another slice for the book's title
                slice_3 = i.find('a').get('href')[9:]
                # Now we can get the full url for each product in this category...
                new_url = f'{site}{slice_1}{slice_3}'
                # and store them
                all_url.append(new_url)
                
book_infos = {}
#   We can now retrieve information from all books by iterating through our list :
for url in all_url:

#-----------------------------------------------#
#   STEP ONE : GET BOOK INFO FOR ONE ELEMENT :  #
#-----------------------------------------------#

    # Now we can replace soup by our fucntion
    for element in read_url(url).findAll('div',{'class': 'container-fluid page'}):
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
        
        d = str(read_url(url).findAll('meta', attrs={'name': 'description'}))
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
df.to_csv('Nonfiction.csv')