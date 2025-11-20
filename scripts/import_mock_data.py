# Module : import_mock_data
# Purpose : script connecting the function that fetches the products (at the moment just from the mock) to the function that repeat another function
# who execute the SQL query insert_product
# A script is a file who contains a series of commands automatically executed. Usually import data, create backups, tests, create simulations

from app.services.shopify_connector import fetch_products_from_shopify_mock
from app.database.queries import import_mock_products

if __name__ == "__main__":
    products = fetch_products_from_shopify_mock()
    import_mock_products(products)
    print("Products successfully imported")