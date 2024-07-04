import asyncio
import re
from requests import post
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


AMAZON = "https://amazon.ae"

URLS = {
    AMAZON: {
        "product_selector": "div.s-card-container"
    }
}

available_urls = URLS.keys()

async def get_number_of_pages(url, driver, search_text):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    try:
        page_nums_span = str(soup.find_all('span',{'class':'s-pagination-item s-pagination-disabled'})[0])
    except:
        page_nums_span = str(soup.find_all('span',{'class':'s-pagination-strip'}))
        
    last_page_num = re.findall(r'>(\d+)</', page_nums_span)[-1]
    return int(last_page_num)


async def search(metadata, driver, search_text):
    print(f"Searching for {search_text} on Amazon")
    url = AMAZON + "/s?k=" + search_text
    search_text = search_text.replace(' ','+')
    num_pgs = await get_number_of_pages(url, driver, search_text)
    print("No pgs:", num_pgs)
    products = []
    for i in range(1, num_pgs + 1):
        url = url + "&page=" + str(i)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        result_container = soup.find_all('div',{'class':'s-main-slot s-result-list s-search-results sg-row'})
        
        
        for container in result_container:
            items = container.find_all('div', {'data-component-type': 's-search-result'})
            for item in items:
                
                title = item.h2.text.strip()
                
                try:
                    link = AMAZON + item.h2.a['href']
                except:
                    h2 = item.find_all('h2')[1]
                    link = AMAZON + h2.a['href']
                try:
                    price = item.find('span', class_='a-price-whole').text.strip()
                except:
                    price = "Price not available"
                
                image_tag = item.find('img', {'class': 's-image'})
                
                image_link = image_tag['src'] if image_tag else "Image not available"
                
                products.append({
                    "title": title,
                    "link": link,
                    "price": price,
                    "image_link":image_link
                })
    print(f"No. of products retrived : {len(products)}")
    return products



async def search_amazon(search_text, url = AMAZON):
    metadata = URLS.get(url)
    if not metadata:
        print("Invalid URL.")
        return

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches',['enable-logging'])

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = webdriver.Chrome(options=options)

    search_results = await search(metadata, driver, search_text)
    driver.quit()
    return search_results

if __name__ == "__main__":
    # test script
    asyncio.run(search_amazon(AMAZON, "iPhone 11")) #ryzen 9 3950x