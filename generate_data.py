import os
import duckdb
import pandas as pd
import random
from faker import Faker
import logging

fake = Faker()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Get the number of records to generate from an environment variable (robust parsing)
_num_records_raw = os.getenv("NUM_RECORDS", "")
if not _num_records_raw:
    num_records = 1000
else:
    try:
        num_records = int(_num_records_raw)
    except ValueError:
        logging.warning(
            f"NUM_RECORDS env var value '{_num_records_raw}' is not an int. Falling back to 1000."
        )
        num_records = 1000
logging.info(f"Generating {num_records} records for each use case.")


# 1. Generate Fake User Profiles
def generate_user_profile(sno: int):
    """Generate a single user profile.

    sno: sequential integer starting at 1 (acts as a stable row number)
    """
    profile = {
        "sno": sno,
        "user_id": fake.uuid4(),
        "fullname": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "address": fake.address(),
        "phone_number": fake.phone_number(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=90),
        "created_at": fake.date_time_this_decade(),
        "location": fake.city(),
    }
    logging.debug(f"Generated user profile: {profile}")
    return profile


# 2. Generate Fake Product Data
def generate_product():
    product = {
        "product_id": fake.uuid4(),
        "product_name": fake.word().capitalize(),
        "category": random.choice(["Electronics", "Clothing", "Books", "Toys"]),
        "price": round(random.uniform(10, 1000), 2),
        "stock": random.randint(0, 500),
        "description": fake.text(max_nb_chars=200),
        "created_at": fake.date_time_this_year(),
    }
    logging.debug(f"Generated product: {product}")
    return product


# 3. Generate Fake Financial Transactions
def generate_transaction(user_ids, product_ids):
    transaction = {
        "transaction_id": fake.uuid4(),
        "user_id": random.choice(user_ids),  # Use a user_id from the user_profiles
        "product_id": random.choice(product_ids),  # Use a product_id from the products
        "amount": round(random.uniform(10, 10000), 2),
        "transaction_type": random.choice(["Credit", "Debit"]),
        "date": fake.date_time_this_year(),
        "description": fake.sentence(nb_words=6),
    }
    logging.debug(f"Generated transaction: {transaction}")
    return transaction


# Generate user profiles first, so we have user_ids to link with transactions
logging.info("Starting to generate user profiles.")
user_profiles = [generate_user_profile(i + 1) for i in range(num_records)]
logging.info("Extract user_ids for foreign key relationships")
user_ids = [user["user_id"] for user in user_profiles]
logging.info("Finished generating user profiles.")

logging.info("Starting to generate products.")
products = [generate_product() for _ in range(num_records)]
logging.info("Extract product_ids for foreign key relationships")
product_ids = [product["product_id"] for product in products]
logging.info("Finished generating products.")

logging.info("Starting to generate transactions linked to user profiles and products.")
transactions = [generate_transaction(user_ids, product_ids) for _ in range(num_records)]
logging.info("Finished generating transactions.")

logging.info("Converting generated data to DataFrames.")
user_profiles_df = pd.DataFrame(user_profiles)
products_df = pd.DataFrame(products)
transactions_df = pd.DataFrame(transactions)

# Save DataFrames to CSV
logging.info("Saving DataFrames to CSV files.")
user_profiles_df.to_csv("user_profiles.csv", index=False)
products_df.to_csv("products.csv", index=False)
transactions_df.to_csv("transactions.csv", index=False)

# Filter the list to include only .csv files
all_files = os.listdir(os.getcwd())
files = [file for file in all_files if file.endswith(".csv")]

logging.info("Converting CSV files into DuckDB tables.")
con = duckdb.connect("sampledata_duckdb.db")
for file in files:
    table_name = os.path.splitext(file)[
        0
    ]  # Remove .csv extension to get the table name
    con.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS (SELECT * FROM read_csv_auto('{file}', delim=',', header=true))"
    )
    print(f"Table {table_name} created in DuckDB using {file}.")
con.close()
