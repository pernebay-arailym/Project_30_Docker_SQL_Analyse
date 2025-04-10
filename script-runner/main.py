import csv
import sqlite3

# # Function to create the SQLite database and tables
def create_database():
    # Create a connection to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    # Create table for products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER
        )
    ''')

    # Add stock column if it doesn't exist
    # cursor.execute("PRAGMA table_info(products)")
    # columns = [row[1] for row in cursor.fetchall()]
    # if "stock" not in columns:
    #     cursor.execute("ALTER TABLE products ADD COLUMN stock INTEGER")

    # Create table for stores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            store_id INTEGER PRIMARY KEY,
            city TEXT NOT NULL,
            employee_count INTEGER NOT NULL
        )
    ''')

    # Add store_id column if it doesn't exist
    # cursor.execute("PRAGMA table_info(sales)")
    # columns = [row[1] for row in cursor.fetchall()]
    # if "store_id" not in columns:
    #     cursor.execute("ALTER TABLE sales ADD COLUMN store_id INTEGER")
    #     cursor.execute("ALTER TABLE sales ADD FOREIGN KEY (product_id) REFERENCES products (product_id)")
    #     cursor.execute("ALTER TABLE sales ADD FOREIGN KEY (store_id) REFERENCES stores (store_id)")

    # Create table for sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_date TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            store_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (product_id),
            FOREIGN KEY (store_id) REFERENCES stores (store_id)
        )
    ''')

    # Create table for analysis results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY,
            analysis_name TEXT,
            result TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and tables created successfully.")


def import_data_to_db():
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    # Import product data
    with open('produit.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                product_id = row['ID Référence produit']
                product_name = row['Nom']
                price_str = row['Prix'].replace(',', '.').strip() #added strip()
                print(f"raw price string: {price_str}") #added print statement
                price = float(price_str)
                stock = int(row['Stock'])
                print(f"Inserting product: {product_id}, {product_name}, {price}, {stock}")
                cursor.execute('''
                    INSERT OR IGNORE INTO products (product_id, product_name, price, stock)
                    VALUES (?, ?, ?, ?)
                ''', (product_id, product_name, price, stock))
            except ValueError as e:
                print(f"Error processing product: {row} -> {e}")
            except sqlite3.IntegrityError as e:
                print(f"SQLite Error processing product: {row} -> {e}")

    # Import store data
    with open('magasin.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                store_id = int(row['ID Magasin'])
                city = row['Ville']
                employee_count = int(row['Nombre de salariés'])
                cursor.execute('''
                    INSERT OR IGNORE INTO stores (store_id, city, employee_count)
                    VALUES (?, ?, ?)
                ''', (store_id, city, employee_count))
            except ValueError as e:
                print(f"Error processing store: {row} -> {e}")
            except sqlite3.IntegrityError as e:
                print(f"SQLite Error processing store: {row} -> {e}")

    # Import sales data
    with open('vent.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sale_date = row['Date']
                product_id = row['ID Référence produit']
                quantity = int(row['Quantité'])
                cursor.execute('''
                    INSERT OR IGNORE INTO sales (sale_date, product_id, quantity, store_id)
                    VALUES (?, ?, ?, ?)
                ''', (sale_date, product_id, quantity, store_id))
            except ValueError as e:
                print(f"Error processing sale: {row} -> {e}")
            except sqlite3.IntegrityError as e:
                print(f"SQLite Error processing sale: {row} -> {e}")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Data imported successfully.")

def create_analysis_table():
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY,
            analysis_name TEXT,
            result TEXT
        )
    ''')

    conn.commit()
    conn.close()

def store_analysis_result(analysis_name, result):
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO analysis_results (analysis_name, result)
        VALUES (?, ?)
    ''', (analysis_name, result))

    conn.commit()
    conn.close()

# Total revenue across all sales
def total_revenue():
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT SUM(s.quantity * p.price) AS total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
    ''')

    total = cursor.fetchone()[0]
    conn.close()
    return total

# Total sales by product (name)
def sales_by_product():
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.product_name, SUM(s.quantity) AS total_quantity, SUM(s.quantity * p.price) AS total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        GROUP BY p.product_name
    ''')

    products = cursor.fetchall()
    conn.close()
    return products

# Total sales by city
def sales_by_city():
    conn = sqlite3.connect('/data/sales_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT m.city, SUM(s.quantity * p.price) AS total_revenue
        FROM sales s
        JOIN stores m ON s.store_id = m.store_id
        JOIN products p ON s.product_id = p.product_id
        GROUP BY m.city
    ''')

    cities = cursor.fetchall()
    conn.close()
    return cities

def print_analysis_results():
    conn = sqlite3.connect('/data/sales_data.db') #correct the path
    cursor = conn.cursor()

    cursor.execute("SELECT analysis_name, result FROM analysis_results")
    results = cursor.fetchall()

    if results:
        print("Analysis Results:")
        for name, result in results:
            print(f"- {name}: {result}")
    else:
        print("No analysis results found.")

    conn.close()

def main():
    create_database()
    # Run the analysis
    create_analysis_table()  # Create the analysis_results table

    # Import data before running analysis
    import_data_to_db()

    # Analyze and store total revenue
    total = total_revenue()
    print('total :', total)
    store_analysis_result("Total Revenue", f"Total Revenue: {total:.2f} EUR")

    # Analyze and store sales by product
    sales_by_product_results = sales_by_product()
    for result in sales_by_product_results:
        store_analysis_result(f"Sales by Product - {result[0]}", 
                              f"Quantity Sold: {result[1]}, Revenue: {result[2]:.2f} EUR")

    # Analyze and store sales by city
    sales_by_city_results = sales_by_city()
    for result in sales_by_city_results:
        store_analysis_result(f"Sales by City - {result[0]}", 
                              f"Total Revenue: {result[1]:.2f} EUR")

    print_analysis_results()

    print("Analysis completed and results stored.")

if __name__ == "__main__":
    main()
