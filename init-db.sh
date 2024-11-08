#!/bin/bash
# This script modifies PostgreSQL configuration files for remote access.

# Allow remote connections by setting listen_addresses to '*'
echo "host    all             all             0.0.0.0/0            md5" >> "$PGDATA/pg_hba.conf"
echo "listen_addresses='*'" >> "$PGDATA/postgresql.conf"