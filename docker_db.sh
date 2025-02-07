#!/bin/bash

# Define variables
NETWORK_NAME="ciclonet"
CONTAINER_NAME="cicloapi_postgis"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="rogerbsc"
POSTGRES_DB="CICLOAPI"
NEW_DB_USER="roger"
NEW_DB_PASSWORD="rogerbsc"
POSTGIS_IMAGE="postgis/postgis:17-3.5"

# Check if the network exists, create if not
if ! docker network ls | grep -q "$NETWORK_NAME"; then
  echo "Creating Docker network: $NETWORK_NAME"
  docker network create "$NETWORK_NAME"
else
  echo "Docker network $NETWORK_NAME already exists"
fi

# Run the PostGIS container
echo "Starting PostGIS container..."
docker run -d \
  --platform linux/amd64 \
  --name "$CONTAINER_NAME" \
  -e POSTGRES_USER="$POSTGRES_USER" \
  -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  -e POSTGRES_DB="$POSTGRES_DB" \
  -p 5433:5432 \
  --network "$NETWORK_NAME" \
  "$POSTGIS_IMAGE"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec "$CONTAINER_NAME" pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
  sleep 2
done
echo "PostGIS is ready."

# Create a new database user
echo "Creating user '$NEW_DB_USER'..."
docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
CREATE USER $NEW_DB_USER WITH PASSWORD '$NEW_DB_PASSWORD';
CREATE DATABASE CICLOAPI;
GRANT ALL PRIVILEGES ON DATABASE CICLOAPI TO roger;
GRANT USAGE, CREATE ON SCHEMA public TO roger;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO roger;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO roger;
EOF

echo "Setup completed successfully."

