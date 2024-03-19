from sqlite3 import Error, connect
from listing import Listing
import pandas as pd


class DatabaseWrapper:
    def __init__(self, db_file):
        """create a database connection to a SQLite database"""
        self.conn = None
        try:
            self.conn = connect(db_file)
            self.conn.row_factory = self.dict_factory
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
        if date_created is not None:
            listing.created = date_created
            listing.last_seen = date_created
            listing.updated = date_created
        cur.execute(sql, [getattr(listing, attr) for attr in columns])
        self.conn.commit()
        return cur.lastrowid

    # https://stackoverflow.com/a/3300514
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


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

    def update_listing(self, listing, created=None, date_updated=None, last_seen=None):
        """
        Update a Listing in the listings table
        """
        attributes = [attr for attr in dir(listing) if not callable(getattr(listing, attr)) and not attr.startswith('__')]
        sql = f"UPDATE listings SET {','.join([f'{attr}=?' for attr in attributes if attr != 'id'])} WHERE id=?"
        cur = self.conn.cursor()
        if date_updated is not None:
            listing.updated = date_updated
        if last_seen is not None:
            listing.last_seen = last_seen
        if created is not None:
            listing.created = created
        attribute_values = [getattr(listing, attr) for attr in attributes if attr != 'id']
        attribute_values.append(listing.id)
        cur.execute(sql, attribute_values)
        self.conn.commit()
        
    def get_df(self):
        return pd.read_sql_query("SELECT * FROM listings", self.conn)


    def close_conn(self):
        if self.conn:
            self.conn.close()
