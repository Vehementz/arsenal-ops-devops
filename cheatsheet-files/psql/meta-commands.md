# psql

psql is the interactive terminal client for PostgreSQL. Its backslash meta-commands list and describe databases, tables, roles and other objects.

#platform/multiple #target/Database #cat/DevOps

% psql, postgresql, meta-commands, describe, list tables, backslash

## psql - List Databases

List all databases on the server.

```
\l
```

## psql - Switch Database

Connect to another database within the same session.

```
\c <database>
```

## psql - List Tables

List tables in the current schema, or use `\dt *.*` for all schemas.

```
\dt
```

## psql - Describe a Table

Show columns, types, indexes and constraints of a table.

```
\d <table>
```

## psql - Describe a Table with Details

Include storage, comments and descriptions.

```
\d+ <table>
```

## psql - List Schemas

List all schemas in the database.

```
\dn
```

## psql - List Roles

List database roles and their attributes.

```
\du
```

## psql - List Views, Indexes and Sequences

List other object types.

```
\dv
\di
\ds
```

## psql - List Functions

List functions in the current database.

```
\df
```

## psql - List Installed Extensions

Show extensions installed in the current database.

```
\dx
```

## psql - Toggle Expanded Output

Print each row as a vertical record, useful for wide tables.

```
\x auto
```

## psql - Toggle Query Timing

Show how long each query takes.

```
\timing
```

## psql - Edit the Last Query in an Editor

Open the query buffer in `$EDITOR`.

```
\e
```

## psql - Save Query Output to a File

Redirect query results to a file, then restore the terminal with a bare `\o`.

```
\o <file>
SELECT * FROM <table>;
\o
```

## psql - Run a Script from Inside psql

Execute a SQL file from the prompt.

```
\i <file.sql>
```

## psql - Get Help

List meta-commands or show SQL syntax help.

```
\?
\h <SQL command>
```

## psql - Quit

Leave the psql session.

```
\q
```
