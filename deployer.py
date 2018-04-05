import sys

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import schema

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python deployer.py postgresql://rootuser:password@postgresql:port/databasse_name")
        exit(1)

    engine = create_engine(sys.argv[1])

    print("Check database existence")
    if not database_exists(engine.url):
        print("Database not exists. Creating.")
        create_database(engine.url)
        print("Database created")

    print("Creating objects")
    schema.metadata.create_all(engine)
    print("Done!")
