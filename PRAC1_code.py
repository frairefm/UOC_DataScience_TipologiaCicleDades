from bs4 import BeautifulSoup, NavigableString
import requests
import pandas as pd

def get_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


# Extracts the links to every review edition
def get_links():
    links = list()
    h2s = soup.findAll('h2', class_='teaser_title')
    for h2 in h2s:
        links.append(h2.a['href'])    
    return links

# Gets into each review edition and into every single article to draw their data out
def extract_items(links):
   
    for link in links:
        soup = get_soup(link)

        ## html structure of 'quaderns' pages
        if("QuadernsICA" not in link):
            # get review title
            print()
            review_title = soup.find('div', class_='page page_issue').h1
            print(review_title.text.strip())
            
            # Gets review description
            review_description = soup.find('div', class_='description').p
            
            # Gets url articles & pages
            ref = soup.findAll('div', class_='title')
            pages = soup.findAll('div', class_='pages')
            for a, pag in zip(ref, pages):
                
                # Appends review_title & review_description to their respective lists for each article
                review_title_list.append(review_title.text.strip())
                review_description_list.append(review_description.text.strip())
                
                # Appends article pages to article_pages_list
                article_pages_list.append(pag.text.strip())
                
                # Explores page article
                inner_soup = get_soup(a.a['href'])
                
                # Gets article title
                article_title = inner_soup.find('h1', class_='page_title')
                article_title_list.append(article_title.text.strip())
                
                # Get article authors
                authors = list()
                article_authors = inner_soup.findAll('span', class_='name')
                for author in article_authors:
                    authors.append(author.text.strip())
                joined_string = ",".join(authors)
                article_authors_list.append(joined_string)
                
                # Get article keywords
                article_keywords = inner_soup.find('span', class_='value')
                if(article_keywords):
                    joined_string = " ".join(article_keywords.text.split())
                    article_keywords_list.append(joined_string)
                else:
                    article_keywords_list.append(None)
                
                # Get article abstract
                article_abstract = inner_soup.find('div', class_='item abstract')
                article_abstract = article_abstract.text.replace('Resum', '').strip()
                article_abstract_list.append(article_abstract)
                
                # Get article pdf
                article_pdf=inner_soup.find('a', class_='obj_galley_link pdf')['href']
                article_pdf_list.append(article_pdf)
        
                print("-" + article_title.text.strip())
        
        ## html structure of 'QuadernsICA' pages
        elif ("QuadernsICA" in link):
          
            # Gets review title
            print()
            review_title = soup.find('li', class_='active')
            print(review_title.text.strip())
            
            # Gets review description
            review_description = soup.find('div', class_='description')   
            
            # Gets url articles & pages
            ref = soup.findAll('h3', class_='media-heading')
            pages = soup.findAll('p', class_='pages') # ok
            for a, pag in zip(ref, pages):
                
                # Appends review_title to review_title_list for each article
                if(review_title):
                    review_title_list.append(review_title.text.strip())
                else:
                    review_title_list.append(None)
                
                # Appends review_description to review_description_list for each article
                if(review_description):
                    review_description_list.append(review_description.text.strip())
                else:
                    review_description_list.append(None) 
                
                # Appends article pages to article_pages_list
                article_pages_list.append(pag.text.strip())
                
                # Explores page article
                inner_soup = get_soup(a.a['href'])
            
                # Gets article title
                article_title = inner_soup.find('h1', class_='page-header')
                if(article_title):              
                    article_title_list.append(article_title.text.strip())
                else:
                    article_title_list.append(None)
                    
                # Gets article authors
                authors = list()
                article_authors = inner_soup.findAll('div', class_='author')
                if(article_authors):
                    for author in article_authors:
                        authors.append(author.find('strong').text)
                    joined_string = ",".join(authors)
                    article_authors_list.append(joined_string)
                else:
                    article_authors_list.append(None)                    
                    
                # Gets article abstract & keywords
                article_abstract = inner_soup.find('div', class_='article-abstract')
                if(article_abstract):
                    article_abstract_list.append(article_abstract.text.strip())
                    article_keywords_list.append(article_abstract.text.strip().partition("Keywords: ")[2])
                else:
                    article_abstract_list.append(None)
                    article_keywords_list.append(None)
                
                # Gets article pdf
                article_pdf=inner_soup.find('a', class_='galley-link btn btn-primary pdf')
                if(article_pdf):
                    article_pdf_list.append(article_pdf['href'])
                else:
                    article_pdf_list.append(None)
                
                print("-" + article_title.text.strip())

# initialization of fields lists
review_title_list = list()
review_description_list = list()
article_title_list = list()
article_pages_list = list()
article_authors_list = list()
article_keywords_list = list()
article_abstract_list = list()
article_pdf_list = list()

print("Start")

# first page
url_page="https://www.antropologia.cat/publicacions-ica/quaderns/"
soup = get_soup(url_page)
links = get_links()
extract_items(links)
next_page = soup.find('a', class_='next page-numbers')

# following pages loop
while(next_page):
    url_page = next_page['href']
    soup = get_soup(url_page)
    links = get_links()
    extract_items(links)
    next_page = soup.find('a', class_='next page-numbers') # ok

print("Extraction done")
print("Setting dataset\n")
print(str(len(article_title_list)) + " articles from " + str(len(set(review_title_list))) + " were retrieved")

# Creates a dataset creation and populates it with field lists data
df = pd.DataFrame({'Review title':review_title_list,
                   'Review description':review_description_list,
                   'Article title':article_title_list,
                   'Article pages':article_pages_list,
                   'Article authors':article_authors_list,
                   'Article keywords':article_keywords_list,
                   'Article abstract':article_abstract_list,
                   'Article pdf':article_pdf_list})

# Writes the files
df.to_csv('Quaderns_ICA.csv', sep='|')
df.to_excel('Quaderns_ICA.xlsx')

print("Dataset written into 'Quaderns_ICA.csv' file")
print("Dataset written into 'Quaderns_ICA.xlsx' file")
print("\nEnd")