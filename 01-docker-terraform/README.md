## Homework 1

### Question 1

```bash
docker run -it --entrypoint=bash python:3.12.8
pip --version
```

### Prepare Postgres

```bash
docker network create pg-network

docker run -d \
--name pg-database \
--network=pg-network \
-e POSTGRES_USER=root \
-e POSTGRES_PASSWORD=root \
-e POSTGRES_DB=ny_taxi \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13

docker build -t taxi_ingest:v001 .

docker run -it \
--network=pg-network \
taxi_ingest:v001 \
--user=root \
--password=root \
--host=pg-database \
--port=5432 \
--database=ny_taxi \
--table=green_tripdata \
--file_url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

or

```bash
docker-compose up -d
```

### Question 3

```sql
SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance <= 1
AND lpep_pickup_datetime >= '2019-10-01'
AND lpep_dropoff_datetime < '2019-11-01';

SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance > 1
AND trip_distance <= 3
AND lpep_pickup_datetime >= '2019-10-01'
AND lpep_dropoff_datetime < '2019-11-01';

SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance > 3
AND trip_distance <= 7
AND lpep_pickup_datetime >= '2019-10-01'
AND lpep_dropoff_datetime < '2019-11-01';

SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance > 7
AND trip_distance <= 10
AND lpep_pickup_datetime >= '2019-10-01'
AND lpep_dropoff_datetime < '2019-11-01';

SELECT COUNT(*)
FROM green_tripdata
WHERE trip_distance > 10
AND lpep_pickup_datetime >= '2019-10-01'
AND lpep_dropoff_datetime < '2019-11-01';
```

### Question 4

```sql
SELECT
    DATE(lpep_pickup_datetime) AS pickup_day,
    MAX(trip_distance) AS longest_trip_distance
FROM green_tripdata
GROUP BY pickup_day
ORDER BY longest_trip_distance DESC
LIMIT 1;
```

### Question 5

```sql
SELECT "Zone"
FROM green_tripdata
LEFT JOIN zones ON "PULocationID" = "LocationID"
WHERE DATE(lpep_pickup_datetime) = '2019-10-18'
GROUP BY "PULocationID", "Zone"
HAVING SUM("total_amount") > 13000
LIMIT 3;
```

### Question 6

```sql
SELECT  max(tip_amount) as max_tip, "Zone"
FROM green_tripdata
LEFT JOIN zones ON green_tripdata."DOLocationID" = zones."LocationID"
WHERE "PULocationID" = 74
GROUP BY "DOLocationID", "Zone"
ORDER BY max_tip DESC
LIMIT 1;
```