import requests
from lxml import html
import json
import time 
import csv

headers = {
    'authority': 'www.spacenk.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.6',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.spacenk.com', 
    'sec-ch-ua': '"Not A(Brand";v="99", "Brave";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


base_url= 'https://www.spacenk.com'


def get_details(url):
    response = requests.get(url, headers=headers)
    product = html.fromstring(response.text)

    try:
        how_to = product.xpath('//div[@id="product-howApply"]/div/text()')[0].strip()
    except:
        how_to = ''
    
    try:
        ingredients = "||".join(product.xpath('//div[@id="product-ingredients"]/div/text()')[0].strip().split(','))
    except:
        ingredients = ''

    try:
        url_parts = url.split('/')
        category = url_parts[4]
        sub_category = url_parts[5]
        micro_category = url_parts[6]
    except:
        category=''
        sub_category=''
        micro_category=''

    ld = product.xpath('//script[@type="application/ld+json"]/text()')[1]
    dados = json.loads(ld)
    data = {
        'url': url,
        'brand': dados['brand']['name'],
        'name': dados['name'],
        'Product Category': '',
        'Category': category,
        'SubCategory': sub_category,
        'MicroCategory': micro_category,
        'Description': dados['description'],
        'Item/SKU': dados['sku'],
        'Image': dados['image'][0],
        'UPC (gtin13)': dados['gtin13'],
        'Ingredients': ingredients.replace('\n','').replace('"','').replace('\r', ''),
        'How to Use/Apply': how_to.replace('\n','').replace('"','').replace('\r', ''),
        #TODO add anothers fields...
     }
    return(data)

head_lines = False
f_name = 'spacenk_demo.csv'
i = 1 
with open(f_name, 'a') as f:
    while i > 0:
        url= f'https://www.spacenk.com/us/skincare?page={i}'
        response = requests.get(url, headers=headers)
        data = html.fromstring(response.text)

        products = data.xpath("//div[contains(@class,'image-container')]/a/@href")
        for href in products:
            link = f'{base_url}{href}'
            print(f'[{i}]{link}')
            data_fields = get_details(link)
            writer = csv.DictWriter(f, fieldnames=data_fields)
            if head_lines == False:
                head_lines = True
                writer.writeheader()
            writer.writerow(data_fields)
        
        pages = data.xpath("//div[contains(@class,'grid-footer')]/span")
        if len(pages) > 0:
            i = i + 1
        else:
            i = -1 #stop loop, last page 
        time.sleep(1) #can edit to ve more fast or more slow
