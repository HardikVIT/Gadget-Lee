import sqlite3
from sqlite3 import Error
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database connection helper
def create_connection():
    """Creates and returns a connection to the SQLite database."""
    try:
        connection = sqlite3.connect('projet.db')
        return connection
    except Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None

# Insert a new tech item into the tech_items table
def insert_tech_item(product_name, price, product_type):
    """Inserts a new item into tech_items."""
    with create_connection() as connection:
        if connection is None:
            return -1
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO tech_items (product_name, price, product_type) VALUES (?, ?, ?)
            """, (product_name, price, product_type))
            connection.commit()
            logging.info("Tech item inserted successfully!")
            return cursor.lastrowid
        except Error as e:
            logging.error(f"Error inserting tech item: {e}")
            return -1

# Insert a new order
def insert_order(order_id, tech_item_id, price, quantity, product_name):
    """Inserts a new order into the orders table."""
    with create_connection() as connection:
        if connection is None:
            return -1
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO orders (order_id, id, price, quantity, product_name) VALUES (?, ?, ?, ?, ?)
            """, (order_id, tech_item_id, price, quantity, product_name))
            connection.commit()
            logging.info("Order inserted successfully!")
            return cursor.lastrowid
        except Error as e:
            logging.error(f"Error inserting order: {e}")
            return -1

# Insert order status into the transit table
def insert_order_tracking(order_id, status):
    """Inserts a new tracking status into the transit table."""
    with create_connection() as connection:
        if connection is None:
            return -1
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO transit (order_id, status) VALUES (?, ?)
            """, (order_id, status))
            connection.commit()
            logging.info("Order tracking status inserted successfully!")
            return cursor.lastrowid
        except Error as e:
            logging.error(f"Error inserting order tracking: {e}")
            return -1

# Get the total price for a given order
def get_total_order_price(order_id):
    """Calculates and returns the total price for a given order ID."""
    with create_connection() as connection:
        if connection is None:
            return 0
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT SUM(price * quantity) FROM orders WHERE order_id = ?
            """, (order_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
        except Error as e:
            logging.error(f"Error calculating total order price: {e}")
            return 0

# Get the next order ID based on the current maximum
def get_next_order_id():
    """Fetches and returns the next order ID."""
    with create_connection() as connection:
        if connection is None:
            return 1
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT MAX(order_id) FROM orders")
            result = cursor.fetchone()
            return 1 if result[0] is None else result[0] + 1
        except Error as e:
            logging.error(f"Error getting next order ID: {e}")
            return 1

# Get the status of an order from the transit table
def get_order_status(order_id):
    """Fetches and returns the status of a given order."""
    with create_connection() as connection:
        if connection is None:
            return None
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT status FROM transit WHERE order_id = ?", (order_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            logging.error(f"Error fetching order status: {e}")
            return None

# Get item price based on product name
def get_item_price(product_name):
    """Fetches the price of a tech item by its product name."""
    with create_connection() as connection:
        if connection is None:
            return None
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT price FROM tech_items WHERE product_name = ?", (product_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            logging.error(f"Error fetching item price: {e}")
            return None
def get_item_id(product_name):
    """Fetches the price of a tech item by its product name."""
    with create_connection() as connection:
        if connection is None:
            return None
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM tech_items WHERE product_name = ?", (product_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            logging.error(f"Error fetching item price: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Insert a sample tech item
    insert_tech_item("Test Product", 123.45, "Example Type")

    # Get next order ID and create a sample order
    next_order_id = get_next_order_id()
    insert_order(next_order_id, 1, 999.99, 1, "iPhone 15")

    # Add transit status for the order
    insert_order_tracking(next_order_id, "Processing")

    # Fetch and print the total order price and status
    total_price = get_total_order_price(next_order_id)
    print("Total Order Price:", total_price)

    order_status = get_order_status(next_order_id)
    print("Order Status:", order_status)
