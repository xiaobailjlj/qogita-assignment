import pymysql
from datetime import datetime
import logging
import os
import yaml

def load_config(config_file='../conf/config.yaml'):
    config_path = os.path.join(os.path.dirname(__file__), config_file)
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config()
logging.basicConfig(level=getattr(logging, config['logging']['level']))  # INFO, DEBUG, WARNING, ERROR, CRITICAL

class DatabaseHandler:
    def __init__(self, host='localhost', user='qogita', password='qogita1234',
                 database='QOGITA'):
        self.connection_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
        }

    def _get_connection(self):
        return pymysql.connect(
            host=self.connection_params['host'],
            user=self.connection_params['user'],
            password=self.connection_params['password'],
            database=self.connection_params['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def insert_offer_batch(self, offers_data):
        """
        Insert a batch of offers into the database using placeholders.
        :param offers_data: List of dictionaries containing offer data
        :return: None
        """
        logging.info(f"Starting insert_offer_batch: {offers_data}")
        columns = ["uuid", "seller_id", "gtin", "currency", "pack_price", "pack_quantity", "pack_size", "title",
                   "description", "status"]
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO offers ({columns_str}) VALUES ({placeholders})"
        values = []
        for offer_data in offers_data:
            value = (
                offer_data['uuid'],
                offer_data['seller_id'],
                offer_data['gtin'],
                offer_data['currency'],
                offer_data['pack_price'],
                offer_data['pack_quantity'],
                offer_data['pack_size'],
                offer_data['title'],
                offer_data['description'],
                offer_data['status']
            )
            values.append(value)

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                logging.info(f"Executing insert_offer_batch SQL: {sql} with values: {values}")
                cursor.executemany(sql, values)
            connection.commit()
        return

    def get_offer_by_seller_id_and_gtin(self, seller_id, gtin):
        sql = "SELECT * FROM offers WHERE status = 'AVAILABLE'"
        params = []
        if seller_id:
            sql += " AND seller_id = %s"
            params.append(seller_id)
        if gtin:
            sql += " AND gtin = %s"
            params.append(gtin)

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                logging.info(f"Executing get_offer_by_seller_id_and_gtin SQL: {sql} with params: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchall()
        return result

    def delete_offer(self, gtin, seller_id):
        sql = """
        UPDATE offers 
        SET status = 'INVALID'
        WHERE gtin = %s AND seller_id = %s AND status = 'AVAILABLE'
        """

        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                logging.info(f"Executing delete_offer SQL: {sql} with gtin: {gtin}, seller_id: {seller_id}")
                cursor.execute(sql, (gtin, seller_id))
                affected_rows = cursor.rowcount
            connection.commit()

        return affected_rows > 0