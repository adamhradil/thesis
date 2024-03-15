from sqlite3 import Error, connect
from listing import Listing
import pandas as pd


class DatabaseWrapper:
    def __init__(self, db_file):
        """create a database connection to a SQLite database"""
        self.conn = None
        try:
            self.conn = connect(db_file)
        except Error as e:
            print(e)

    def create_table(self):
        """create a table from the create_table_sql statement"""
        try:
            c = self.conn.cursor()
            listing = Listing()
            columns = [attr for attr in dir(listing) if not callable(getattr(listing, attr)) and not attr.startswith("__")]
            create_table_sql = f"CREATE TABLE IF NOT EXISTS listings ({','.join(columns)});"
            c.execute(create_table_sql)
        except Error as e:
            print(e)


    def insert_listing(self, listing, date_created):
        """
        Insert a Listing into the listings table
        """

        columns = [attr for attr in dir(listing) if not callable(getattr(listing, attr)) and not attr.startswith("__")]
        placeholders = ','.join(['?' for _ in columns])
        sql = f"INSERT INTO listings({','.join(columns)}) VALUES({placeholders}) "
        cur = self.conn.cursor()
        cur.execute(sql, [getattr(listing, attr) for attr in columns])
        self.conn.commit()
        return cur.lastrowid

    def get_listing(self, listing_id):
        """
        Query a Listing by id from the listings table
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM listings WHERE id=?", (listing_id,))

        row = cur.fetchone()

        if row is None:
            return None

        listing = Listing(row)
        return listing

    def remove_listing(self, listing_id):
        """
        Remove a Listing by id from the listings table
        """
        sql = "DELETE FROM listings WHERE id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (listing_id,))
        self.conn.commit()

    def update_listing(self, listing, date_updated):
        """
        Update a Listing in the listings table
        """
        attributes = [attr for attr in dir(listing) if not callable(getattr(listing, attr)) and not attr.startswith('__')]
        sql = f"UPDATE listings SET {','.join([f'{attr}=?' for attr in attributes if attr != 'id'])} WHERE id=?"
        cur = self.conn.cursor()
        attribute_values = [getattr(listing, attr) for attr in attributes if attr != 'id']
        attribute_values.append(listing.id)
        cur.execute(sql, attribute_values)
        self.conn.commit()
        
    def get_df(self):
        return pd.read_sql_query("SELECT * FROM listings", self.conn)


    def close_conn(self):
        if self.conn:
            self.conn.close()
