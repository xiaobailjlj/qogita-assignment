import os
import yaml
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app,
     resources=config['cors']['resources'],
     methods=config['cors']['methods'])

@app.route('/api/v1/offers/get', methods=['GET'])
def get_offers():
    """
    Get offers.
    """
    seller_id = request.args.get('seller_id')
    gtin = request.args.get('gtin')

    offers = dbHandler.get_offer_by_seller_id_and_gtin(seller_id, gtin)
    if offers:
        offers = [dict(offer) for offer in offers]
        return jsonify(offers), 200
    else:
        return jsonify({"message": "No offers found"}), 404


@app.route('/api/v1/offers/delete', methods=['POST'])
def delete_offer():
    """
    Delete an offer.
    """
    data = request.get_json()
    gtin = data.get('gtin')
    seller_id = data.get('seller_id')

    if not gtin or not seller_id:
        return jsonify({"message": "Missing required fields"}), 400

    result = dbHandler.delete_offer(gtin, seller_id)
    if result:
        return jsonify({"message": "Offer deleted successfully"}), 200
    else:
        return jsonify({"message": "Offer not found"}), 404




if __name__ == '__main__':
    server_config = config['server']
    app.run(
        debug=server_config['debug'],
        host=server_config['host'],
        port=server_config['port']
    )