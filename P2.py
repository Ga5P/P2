#   Importing usefull librairies :

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import re
import pandas as pd
import webbrowser
import requests

#   Knowing the browser that we will use :
# In the first time we have to know which OS is used:
webbrowser.get()
result = webbrowser._tryorder
os = result[0][:3]

# Then, indicate appropriates drivers:
if os == 'win':
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    driver = webdriver.Edge(EdgeChromiumDriverManager().install())
else :
    if result[1] == 'chrome':
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(ChromeDriverManager().install())
    if result[1] == 'firefox':
        from webdriver_manager.firefox import GeckoDriverManager
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    
#   Define the host url and the piece of url wich is present in the product page :

site = "http://books.toscrape.com/"
slice_1 = "catalogue/"

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

#----------------------------------------------------#
#   STEP THREE : GET BOOK INFO FOR ALL CATEGORIES :  #
#----------------------------------------------------#

dic_categories = {}

for categories in read_url(site).findAll('ul',{'class': 'nav nav-list'}):
    
    for a in categories.find_all('a', href=True)[1:]:
        
        # We get what corresponds to 'herf' between a tags
        cat = a['href']
        # we complete the link of the site with the category's slice
        cat_url = f'{site}{cat}'

#------------------------------------------------------#
#   STEP TWO : GET BOOK INFO FOR AN ENTIRE CATEGORY :  #
#------------------------------------------------------#
    
        #   Making an empty list to store all urls of the books in a category :
        all_url = []
        
        
        #   Getting the number of results
        nb_result = int(read_url(cat_url).findAll('strong')[1].get_text())
        
        #   We have 20 results by page, so :
        if nb_result > 20:
            
                    #   Getting the number of pages
                    page_number = int(read_url(cat_url).find('li',{'class': 'current'})
                                          .text.replace(" ","").replace("\n",'')[-1])
            
                    # The site's structure allows to replace "index.html" at the first page to "page-1.html"
                    # we can make a slice by removing the end
                    slice_2 = cat_url[:-len("index.html")-1]
                    
                    # The range goes from page 1 to page 6
                    list_pages = range(1, page_number+1)
                    # A generator with a format string allows to have all end of urls in our category
                    list_pages = [f"/page-{p}.html" for p in list_pages]
                    # And another one to get all entires urls for the category results
                    pages_url = [f'{slice_2}{p}' for p in list_pages]
        
        #   If there is only one result page, we just keep the category's url
        else:
                    pages_url = []
                    pages_url.append(cat_url)
        
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
                
                
#----------------------------------------#
#   STEP FOUR : DOWNLOAD BOOK'S IMAGE :  #
#----------------------------------------#
    
                pic = requests.get(image_url)
                
                if os =='win':
                    # There is more unaccepted characters under Windows:
                    pic_title = re.sub('[<>:"/\|?*]', ' ', title)                    
                else:
                    # Just one here:
                    pic_title = title.replace('/', ' ')
                    
                if title in book_infos.keys():
                    pic_title = pic_title + " -bis"
                    # These lines allow to rename a title present twice wich give us an incomplete result

                #   Making a new png file for each image:
                open(f'./{pic_title}.png', 'wb').write(pic.content)
        
                
                infos = [product_page_url, upc, price_including_tax, price_excluding_tax,
                        number_available, title, category, review_rating, image_url,
                        product_description]
                # We making a list with all our recovered infos
                
                book_info = {inf: var for inf,var in zip(wanted_info, infos)}
                # We stock the result in a dictionnary to keep the association {wanted_info : info}
                # from our two lists
                
                if title in book_infos.keys():
                    title = title + " -bis"
                # These lines allow to rename a title present twice wich give us an incomplete result
                
                book_infos[title] = book_info   # We can save all informations of this specific book
                                                # in a new dictionnary
                                                
                dic_categories[book_info.get('category')] = book_infos
                # We can now fill the dictionnary with theses categories as keys

dic_frames = {}
for category, values in dic_categories.items():
    
    #   Transform each dictionnary (value) into dataframe for corresponding category (key)
    cat_name = "df_{element}"
    dic_frames[cat_name.format(element=category)] = pd.DataFrame.from_dict(values, orient='index')

#   Making a new csv file for each category
for key in dic_frames.keys():
    dic_frames[key].to_csv(f'{key}.csv')
