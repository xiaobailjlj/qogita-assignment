import os
import yaml
import pandas as pd
import xmltodict
import uuid
import logging
from database.db_handler import DatabaseHandler

def load_config(config_file='../conf/config.yaml'):
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()
logging.basicConfig(level=getattr(logging, config['logging']['level']))  # INFO, DEBUG, WARNING, ERROR, CRITICAL
dbHandler = DatabaseHandler(
    host=config['database']['host'],
    user=config['database']['user'],
    password=config['database']['password'],
    database=config['database']['db']
)

def process_csv_file(file_path, seller_id=None):
    logging.log(logging.NOTSET, f"Processing CSV file: {file_path} with seller_id: {seller_id}")
    if not seller_id:
        logging.error(f"Invalid seller_id from filename: {file_path}")
        return

    df = pd.read_csv(file_path, usecols=["Variant Barcode", "Variant Price", "Variant Inventory Quantity", "Product Title", "Product.custom.pack_size"])

    offers_data = []
    for _, row in df.iterrows():
        # skip records with empty required fields
        if pd.isna(row["Variant Barcode"]) or pd.isna(row["Variant Price"]) or pd.isna(row["Variant Inventory Quantity"]) or pd.isna(row["Product.custom.pack_size"]):
            logging.warning(f"Skipping row with missing required fields: {row}")
            continue
        # uuid, seller_id, gtin, currency, price, quantity, title, description, status
        offer_data = {
            'uuid': str(uuid.uuid4()),
            'seller_id': seller_id,
            'gtin': str(row["Variant Barcode"]),
            'currency': 'EUR',
            'pack_price': float(row["Variant Price"]),
            'pack_quantity': int(row["Variant Inventory Quantity"]),
            'pack_size': int(row["Product.custom.pack_size"]),
            'title': str(row["Product Title"]),
            'description': '',
            'status': 'AVAILABLE'
        }
        offers_data.append(offer_data)

    try:
        dbHandler.insert_offer_batch(offers_data)
    except Exception as e:
        logging.error(f"Error inserting batch: {e}")

def process_xml_file(file_path, seller_id=None):
    logging.log(logging.NOTSET, f"Processing XML file: {file_path} with seller_id: {seller_id}")
    if not seller_id:
        logging.error(f"Invalid seller_id from filename: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()
    offers_raw = xmltodict.parse(xml_content)['productFeed']['items']['item']

    offers_data = []
    for offer in offers_raw:
        # skip records with empty required fields
        if not offer.get("articleEAN") or not offer.get("currency") or not offer.get("priceWithoutVat") or not offer.get("stockQuantity"):
            logging.warning(f"Skipping row with missing required fields: {offer}")
            continue
        offer_data = {
            'uuid': str(uuid.uuid4()),
            'seller_id': seller_id,
            'gtin': offer['articleEAN'],
            'currency': offer['currency'],
            'pack_price': float(offer['priceWithoutVat']),
            'pack_quantity': int(offer["stockQuantity"]),
            'pack_size': 1,  # assuming pack size is 1 for XML
            'title': offer["articleName"],
            'description': '',
            'status': 'AVAILABLE'
        }
        offers_data.append(offer_data)

    try:
        dbHandler.insert_offer_batch(offers_data)
    except Exception as e:
        logging.error(f"Error inserting batch: {e}")

if __name__ == '__main__':
    # file_list_csv = []
    # file_list_xml = []

    # file_list_csv = ['mock_data.csv']
    # file_list_xml = ['mock_data.xml']

    file_list_csv = ['sample_cosmetics_stocklist.csv']
    file_list_xml = ['wholesale-feed-czW3E2g72cISgDaqJGx5.xml']

    for file in file_list_csv:
        process_csv_file(file, "sellerA")
    for file in file_list_xml:
        process_xml_file(file, "sellerB")

