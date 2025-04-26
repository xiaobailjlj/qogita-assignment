# Offers Management

## Description
A simple Flask API for managing product offers. 

- Provide script to load the provided csv and xml files from the disk and store in MySQL
- Provide a REST API to list all Offers
- Provide a REST API to delete a specific Offer

## Quick Start

1. **Set up MySQL:**
   ```bash
   ./database/init.sql
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Import data:**
   ```bash
   python ./data/import_data.py
   ```

4. **Run the application:**
   ```bash
   python ./app/app.py
   ```
   You can change configuration in ./conf/config.yaml, the server will run at http://localhost:7700 by default.



## API Usage

- **Get offers:** GET `/api/v1/offers/get?seller_id=sellerA&gtin=1234567890123`
- **Delete offer:** POST `/api/v1/offers/delete` with JSON body `{"seller_id": "sellerA", "gtin": "1234567890123"}`