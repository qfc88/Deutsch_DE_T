#!/bin/bash
set -e

# Create postgres user with superuser privileges if it doesn't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
            CREATE USER postgres WITH SUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD '$POSTGRES_PASSWORD';
        ELSE
            ALTER USER postgres PASSWORD '$POSTGRES_PASSWORD';
        END IF;
    END
    \$\$;
    
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO postgres;
EOSQL

echo "Database initialization completed successfully"