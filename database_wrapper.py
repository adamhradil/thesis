from sqlite3 import Error, connect
from listing import Listing


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
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS listings (
                    id text PRIMARY KEY,
                    address text,
                    area integer,
                    available_from text,
                    description text,
                    disposition text,
                    floor text,
                    furnished text,
                    rent text,
                    security_deposit text,
                    service_fees text,
                    status text,
                    type text,
                    url text,
                    balcony text,
                    cellar text,
                    front_garden text,
                    terrace text,
                    elevator text,
                    parking text,
                    garage text,
                    pets text,
                    loggie text,
                    public_transport text
                );
            """
            )
        except Error as e:
            print(e)

    def insert_listing(self, listing):
        """
        Insert a Listing into the listings table
        """
        sql = """ INSERT INTO listings(id,address,area,available_from,
                  description,disposition,floor,furnished,rent,
                  security_deposit,service_fees,status,type,url,
                  balcony,cellar,front_garden,terrace,elevator,
                  parking,garage,pets,loggie,public_transport)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """
        cur = self.conn.cursor()
        cur.execute(
            sql,
            (
                listing.id,
                listing.address,
                listing.area,
                listing.available_from,
                listing.description,
                listing.disposition,
                listing.floor,
                listing.furnished,
                listing.rent,
                listing.security_deposit,
                listing.service_fees,
                listing.status,
                listing.type,
                listing.url,
                listing.balcony,
                listing.cellar,
                listing.front_garden,
                listing.terrace,
                listing.elevator,
                listing.parking,
                listing.garage,
                listing.pets,
                listing.loggie,
                listing.public_transport,
            ),
        )
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

    def update_listing(self, listing):
        """
        Update a Listing in the listings table
        """
        sql = """ UPDATE listings
                  SET address = ?,
                      area = ?,
                      available_from = ?,
                      description = ?,
                      disposition = ?,
                      floor = ?,
                      furnished = ?,
                      rent = ?,
                      security_deposit = ?,
                      service_fees = ?,
                      status = ?,
                      type = ?,
                      url = ?,
                      balcony = ?,
                      cellar = ?,
                      front_garden = ?,
                      terrace = ?,
                      elevator = ?,
                      parking = ?,
                      garage = ?,
                      pets = ?,
                      loggie = ?,
                      public_transport = ?
                  WHERE id = ?"""
        cur = self.conn.cursor()
        cur.execute(
            sql,
            (
                listing.address,
                listing.area,
                listing.available_from,
                listing.description,
                listing.disposition,
                listing.floor,
                listing.furnished,
                listing.rent,
                listing.security_deposit,
                listing.service_fees,
                listing.status,
                listing.type,
                listing.url,
                listing.balcony,
                listing.cellar,
                listing.front_garden,
                listing.terrace,
                listing.elevator,
                listing.parking,
                listing.garage,
                listing.pets,
                listing.loggie,
                listing.public_transport,
                listing.id,
            ),
        )
        self.conn.commit()

    def close_conn(self):
        if self.conn:
            self.conn.close()
