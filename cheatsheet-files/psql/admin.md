# psql

psql is the interactive terminal client for PostgreSQL. It is also used for everyday administration: users, databases, imports, exports and backups.

#platform/multiple #target/Database #cat/DevOps

% psql, postgresql, admin, backup, restore, copy, users, pg_dump

## psql - Create a Database

Create a new database.

```
CREATE DATABASE <database> OWNER <user>;
```

## psql - Create a User

Create a role that is allowed to log in.

```
CREATE USER <user> WITH PASSWORD '<password>';
```

## psql - Grant Privileges on a Database

Give a user full access to a database.

```
GRANT ALL PRIVILEGES ON DATABASE <database> TO <user>;
```

## psql - Change a User Password

Set a new password for an existing role.

```
ALTER USER <user> WITH PASSWORD '<new-password>';
```

## psql - Drop a Database

Delete a database. It must have no active connections.

```
DROP DATABASE <database>;
```

## psql - Show Database and Table Sizes

Report on-disk sizes.

```
SELECT pg_size_pretty(pg_database_size('<database>'));
SELECT pg_size_pretty(pg_total_relation_size('<table>'));
```

## psql - Show Active Connections

List running sessions and their current queries.

```
SELECT pid, usename, datname, state, query FROM pg_stat_activity;
```

## psql - Terminate a Connection

Stop a session by its process ID.

```
SELECT pg_terminate_backend(<pid>);
```

## psql - Export a Table to CSV

Write query results to a local CSV file with a header row.

```
\copy (SELECT * FROM <table>) TO '<file.csv>' WITH CSV HEADER
```

## psql - Import a CSV into a Table

Load a local CSV file into an existing table.

```
\copy <table> FROM '<file.csv>' WITH CSV HEADER
```

## psql - Dump a Database

Create a plain SQL backup with `pg_dump`.

```
pg_dump -h <host> -U <user> -d <database> > <backup.sql>
```

## psql - Dump a Database in Custom Format

Create a compressed backup that `pg_restore` can restore selectively.

```
pg_dump -h <host> -U <user> -Fc -d <database> -f <backup.dump>
```

## psql - Restore a SQL Dump

Load a plain SQL backup into a database.

```
psql -h <host> -U <user> -d <database> -f <backup.sql>
```

## psql - Restore a Custom-Format Dump

Restore a backup made with `-Fc`.

```
pg_restore -h <host> -U <user> -d <database> <backup.dump>
```

## psql - Dump All Databases

Back up every database and global objects such as roles.

```
pg_dumpall -h <host> -U <user> > <all.sql>
```
