import os
import pandas as pd
from sqlalchemy import create_engine
import argparse
import time

parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

parser.add_argument('--user', type=str, help='Postgres user')
parser.add_argument('--password', type=str, help='Postgres password')
parser.add_argument('--host', type=str, help='Postgres host')
parser.add_argument('--port', type=str, help='Postgres port')
parser.add_argument('--database', type=str, help='Postgres database')
parser.add_argument('--table', type=str, help='Postgres table')
parser.add_argument('--file_url', type=str, help='CSV file URL')

args = parser.parse_args()

data_file = "./data.csv.gz"
zones_file = "./taxi_zone_lookup.csv"

os.system(f"wget -O {data_file} {args.file_url}")
os.system(
    f"wget -O {zones_file} https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv")

connection_string = f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
engine = create_engine(connection_string)


def ingest_data(df, table_name, engine):
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False,
            schema='public',
            chunksize=20000,
            method='multi'
        )
        print(f"Successfully sent {len(df)} rows to {table_name}")
    except Exception as e:
        print(f"Failed to send data to Postgres: ${str(e)}")
        raise e


df_iter = pd.read_csv(data_file, iterator=True, chunksize=100000,
                      parse_dates=['lpep_dropoff_datetime', 'lpep_pickup_datetime'],
                      compression='gzip')

try:
    for df_chunk in df_iter:
        start_time = time.time()

        ingest_data(df_chunk, args.table, engine)

        end_time = time.time()
        print(f"Time taken: {end_time - start_time}")

    df_zones = pd.read_csv(zones_file)
    df_zones.to_sql(
        name='zones',
        con=engine,
        if_exists='append',
        index=False,
        schema='public'
    )
except Exception as e:
    print(f"Failed to ingest data: ${str(e)}")
finally:
    engine.dispose()
