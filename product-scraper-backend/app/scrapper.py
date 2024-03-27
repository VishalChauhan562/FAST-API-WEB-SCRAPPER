from datetime import datetime
from typing import Any
import json

import requests
from bs4 import BeautifulSoup as Soup
from pytz import timezone, UTC
import redis
import time

URL = 'https://dentalstall.com/shop/page'
TIMEZONE = 'Asia/Kolkata'


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def extract_product_info(html_content):
    product_list = []
    cards = html_content.find_all('li', class_='product') 
    for card in cards:
        product_title_elem = card.find('h2', class_='woo-loop-product__title')
        product_title = product_title_elem.text.strip() if product_title_elem else ''
        
        product_link = product_title_elem.find('a')['href'] if product_title_elem else ''
        product_id = product_link.split('/')[-2] if product_link else ''
        
        product_price_elem = card.find('span', class_='woocommerce-Price-amount')
        product_price_str = product_price_elem.text.strip() if product_price_elem else ''
        product_price = float(product_price_str.split('₹')[1].replace(',', '')) if product_price_str else 0.0
        
        image_url_elem = card.find('img', class_='attachment-woocommerce_thumbnail')
        image_url = image_url_elem['src'].strip() if image_url_elem else ''
        
        if image_url.startswith('data:image'):
            image_url = image_url_elem['data-lazy-src'].strip() if image_url_elem else ''

        product_info = {
            "product_id": product_id,
            "product_title": product_title,
            "product_price": product_price,
            "path_to_image": image_url
        }
        product_list.append(product_info)

    return product_list


def update_redis_and_json(product_list):
    new_data_count = 0
    updated_data_count = 0

    try:
        with open("product_data.json", "r") as json_file:
            data = json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []

    for product in product_list:
        product_id = product["product_id"]
        cached_price = redis_client.hget(product_id, "product_price")

        if cached_price is not None and float(cached_price) == product["product_price"]:
            continue

        existing_product = next((item for item in data if item["product_id"] == product_id), None)

        if existing_product:
            if existing_product["product_price"] != product["product_price"]:
                existing_product["product_price"] = product["product_price"]
                existing_product["last_updated"] = datetime.now(UTC).astimezone(timezone(TIMEZONE)).isoformat()
                existing_product["path_to_image"] = product["path_to_image"]  # Update path_to_image
                redis_client.hmset(product_id, {
                    "product_price": product["product_price"],
                    "last_updated": existing_product["last_updated"],
                    "path_to_image": product["path_to_image"]
                })
                updated_data_count += 1
        else:
            data.append({
                "product_id": product_id,
                "product_title": product["product_title"],
                "product_price": product["product_price"],
                "last_updated": datetime.now(UTC).astimezone(timezone(TIMEZONE)).isoformat(),
                "path_to_image": product["path_to_image"]  
            })
            redis_client.hmset(product_id, {
                "product_price": product["product_price"],
                "last_updated": datetime.now(UTC).astimezone(timezone(TIMEZONE)).isoformat(),
                "path_to_image": product["path_to_image"]
            })
            new_data_count += 1

    with open("product_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    return new_data_count, updated_data_count


def scrapped_products(page: int) -> dict:
    try:
        page_num = int(page)
        all_product_data = []
        retry_attempts = 3  
        retry_delay = 5 

        for page in range(1, page_num + 1):
            for attempt in range(retry_attempts):
                request = requests.get(f'{URL}/{page}')
                if request.status_code == 200:
                    break 
                else:
                    print(f"Error accessing page {page}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay) 

            html = Soup(request.content, 'html.parser')
            product_data = extract_product_info(html)
            all_product_data.extend(product_data)

        new_count, updated_count = update_redis_and_json(all_product_data)
        total_products = len(all_product_data)

        return {
            "message": f"Data is successfully extracted",
            "total_products" :total_products,
            "new_products_count" : new_count,
            "updated_products_count" : updated_count,
            "result" : all_product_data
        }
    except Exception as e:
        error_message = str(e)
        return {
            "error": error_message
        }
