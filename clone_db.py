#!/usr/bin/env python3
"""
Script to clone a PostgreSQL database schema to a new database.

Usage:
    python clone_db.py new_database_name
"""
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

def parse_db_url(db_url):
    """Parse database URL into connection parameters."""
    result = urlparse(db_url)
    return {
        'dbname': result.path[1:],  # Remove leading '/'
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }

def create_database(conn_params, new_dbname):
    """Create a new database."""
    # Connect to postgres database to create the new database
    conn = psycopg2.connect(
        dbname='postgres',
        user=conn_params['user'],
        password=conn_params['password'],
        host=conn_params['host'],
        port=conn_params['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists and drop if it does
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (new_dbname,))
    if cursor.fetchone():
        print(f"Dropping existing database: {new_dbname}")
        cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(new_dbname)))
    
    # Create new database
    print(f"Creating new database: {new_dbname}")
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_dbname)))
    cursor.close()
    conn.close()

def clone_database(source_params, target_dbname):
    """Clone database schema using pg_dump and psql."""
    # Build connection strings
    source_conn_str = f"postgresql://{source_params['user']}:{source_params['password']}@{source_params['host']}:{source_params['port']}/{source_params['dbname']}"
    target_conn_str = f"postgresql://{source_params['user']}:{source_params['password']}@{source_params['host']}:{source_params['port']}/{target_dbname}"
    
    # Dump schema and data
    print(f"Dumping schema and data from {source_params['dbname']}...")
    dump_cmd = [
        'pg_dump',
        '--no-owner',
        '--no-privileges',
        '--schema-only',  # Only schema, no data
        '--dbname', source_conn_str
    ]
    
    # Restore to new database
    print(f"Restoring to {target_dbname}...")
    psql_cmd = ['psql', '--dbname', target_conn_str]
    
    try:
        dump_process = subprocess.Popen(dump_cmd, stdout=subprocess.PIPE)
        subprocess.check_call(psql_cmd, stdin=dump_process.stdout)
        dump_process.wait()
        print(f"Successfully cloned database schema to {target_dbname}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning database: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python clone_db.py new_database_name")
        sys.exit(1)
    
    source_db_url = "postgres://dave:punter89@localhost:5432/shaboom"
    target_dbname = sys.argv[1]
    
    # Parse source database URL
    source_params = parse_db_url(source_db_url)
    
    # Create and clone database
    create_database(source_params, target_dbname)
    clone_database(source_params, target_dbname)

if __name__ == "__main__":
    main()
