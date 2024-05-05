from sqlite3 import Error, connect
import pandas as pd  # pylint: disable=import-error
from listing import Listing


class DatabaseWrapper:
    """
    A class that provides methods to interact with a SQLite listings database.
    """

    def __init__(self, db_file):
        """
        Initialize the DatabaseWrapper object.

        Parameters:
        - db_file (str): The path to the SQLite database file.
        """
        self.conn = None
        try:
            self.conn = connect(db_file)
            self.conn.row_factory = self.dict_factory
        except Error as e:
            print(e)

    def create_table(self):
        """
        Create a table in the database based on the attributes of the Listing class.
        """
        if self.conn is None:
            return
        try:
            c = self.conn.cursor()
            listing = Listing()
            columns = [
                attr
                for attr in dir(listing)
                if not callable(getattr(listing, attr)) and not attr.startswith("__")
            ]
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS listings ({','.join(columns)});"
            )
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_listing(self, listing, date_created):
        """
        Insert a Listing object into the listings table.

        Parameters:
        - listing (Listing): The Listing object to be inserted.
        - date_created (str): The date the listing was first found.

        Returns:
        - int: The ID of the inserted listing.
        """
        if self.conn is None:
            return None
        columns = [
            attr
            for attr in dir(listing)
            if not callable(getattr(listing, attr)) and not attr.startswith("__")
        ]
        placeholders = ",".join(["?" for _ in columns])
        sql = f"INSERT INTO listings({','.join(columns)}) VALUES({placeholders}) "
        cur = self.conn.cursor()
        if date_created is not None:
            listing.created = date_created
            listing.last_seen = date_created
            listing.updated = date_created
        cur.execute(sql, [getattr(listing, attr) for attr in columns])
        self.conn.commit()
        return cur.lastrowid

    def dict_factory(self, cursor, row):
        """
        Convert a database row to a dictionary.

        Parameters:
        - cursor: The database cursor.
        - row: The row to be converted.

        Returns:
        - dict: The converted row as a dictionary.
        """
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_listing(self, listing_id):
        """
        Query a Listing by ID from the listings table.

        Parameters:
        - listing_id (int): The ID of the listing to be queried.

        Returns:
        - Listing: The queried Listing object, or None if not found.
        """
        if self.conn is None:
            return None
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM listings WHERE id=?", (listing_id,))

        row = cur.fetchone()

        if row is None:
            return None

        listing = Listing(row)
        return listing

    def remove_listing(self, listing_id):
        """
        Remove a Listing by ID from the listings table.

        Parameters:
        - listing_id (int): The ID of the listing to be removed.
        """
        if self.conn is None:
            return
        sql = "DELETE FROM listings WHERE id=?"
        cur = self.conn.cursor()
        cur.execute(sql, (listing_id,))
        self.conn.commit()

    def update_listing(self, listing, created=None, date_updated=None, last_seen=None):
        """
        Update a Listing in the listings table.

        Parameters:
        - listing (Listing): The Listing object to be updated.
        - created (str): The date the listing was first found.
        - date_updated (str): The date the listing was last updated.
        - last_seen (str): The date the listing was last seen.
        """
        if self.conn is None:
            return
        attributes = [
            attr
            for attr in dir(listing)
            if not callable(getattr(listing, attr)) and not attr.startswith("__")
        ]
        sql = f"UPDATE listings SET {','.join([f'{attr}=?' for attr in attributes if attr != 'id'])} WHERE id=?"
        cur = self.conn.cursor()
        if date_updated is not None:
            listing.updated = date_updated
        if last_seen is not None:
            listing.last_seen = last_seen
        if created is not None:
            listing.created = created
        attribute_values = [
            getattr(listing, attr) for attr in attributes if attr != "id"
        ]
        attribute_values.append(listing.id)
        cur.execute(sql, attribute_values)
        self.conn.commit()

    def delete_old_listings(self, last_crawl_time):
        """
        Delete all listings with a last_seen date older than the last crawl time.

        Parameters:
        - last_crawl_time (str): The last crawl time.
        """
        if self.conn is None:
            return
        sql = "DELETE FROM listings WHERE datetime(last_seen) < datetime(?, '-1 hour')"
        cur = self.conn.cursor()
        cur.execute(sql, (last_crawl_time,))
        deleted_ids = cur.fetchall()
        for listing_id in deleted_ids:
            print(f"Deleted listing with id: {listing_id}")
        self.conn.commit()

    def get_df(self):
        """
        Retrieve all listings from the listings table as a pandas DataFrame.

        Returns:
        - pandas.DataFrame: The retrieved listings as a DataFrame.
        """
        if self.conn is None:
            return None
        self.conn.row_factory = None
        df = pd.read_sql_query("SELECT * FROM listings", self.conn)
        self.conn.row_factory = self.dict_factory
        return df

    def close_conn(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
