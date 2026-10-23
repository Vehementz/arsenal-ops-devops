# psql

psql is the interactive terminal client for PostgreSQL. It connects to a server, runs SQL and exposes backslash meta-commands for inspecting the database.

#platform/multiple #target/Database #cat/DevOps

% psql, postgresql, postgres, connection, client

## psql - Connect to a Database

Connect with explicit host, port, user and database.

```
psql -h <host> -p 5432 -U <user> -d <database>
```

## psql - Connect with a Connection URI

Use a single connection string instead of separate flags.

```
psql "postgresql://<user>:<password>@<host>:5432/<database>?sslmode=require"
```

## psql - Connect as the postgres Superuser

Open a local session as the `postgres` system user.

```
sudo -u postgres psql
```

## psql - Connect Using a Password from the Environment

Avoid the interactive prompt by setting `PGPASSWORD` for a single command.

```
PGPASSWORD=<password> psql -h <host> -U <user> -d <database>
```

## psql - Force a Password Prompt

Prompt for a password even if the server would not ask for one.

```
psql -h <host> -U <user> -d <database> -W
```

## psql - Run a Single Command

Execute one SQL statement or meta-command and exit.

```
psql -d <database> -c "SELECT version();"
```

## psql - Run a SQL File

Execute all statements from a file.

```
psql -d <database> -f <file.sql>
```

## psql - Run a File and Stop on Error

Abort at the first failing statement and wrap the file in one transaction.

```
psql -d <database> -v ON_ERROR_STOP=1 --single-transaction -f <file.sql>
```

## psql - Check Server Connectivity

Check whether the server is accepting connections.

```
pg_isready -h <host> -p 5432
```

## psql - Show Connection Information

Display the current database, user, host and port from inside psql.

```
\conninfo
```
