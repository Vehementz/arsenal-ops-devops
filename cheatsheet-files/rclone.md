# Rclone

Rclone is a command-line program to manage files on cloud storage. It syncs, copies, mounts and serves files across more than 70 storage providers (S3, GCS, Azure Blob, Google Drive, SFTP, etc.).

#platform/multiple #target/Storage #cat/DevOps

% rclone, cloud storage, sync, backup, s3

## Rclone - Check Installation

Verify that rclone is installed.

```
rclone version
```

## Rclone - Configure a Remote

Interactively create a new remote (cloud storage connection).

```
rclone config
```

## Rclone - List Remotes

List the remotes defined in the configuration file.

```
rclone listremotes
```

## Rclone - Show Config File Path

Print the location of the rclone configuration file.

```
rclone config file
```

## Rclone - List Directories

List the top-level directories of a remote path.

```
rclone lsd <remote>:<path>
```

## Rclone - List Files

List objects and their sizes in a remote path.

```
rclone ls <remote>:<path>
```

## Rclone - List Files Detailed

List objects with size, modification time and path.

```
rclone lsl <remote>:<path>
```

## Rclone - Copy Files

Copy files from source to destination, skipping files that are already identical.

```
rclone copy <source> <remote>:<path> --progress
```

## Rclone - Sync Directories

Make the destination identical to the source. Files only present in the destination are deleted.

```
rclone sync <source> <remote>:<path> --progress
```

## Rclone - Dry Run

Preview what a command would do without changing anything.

```
rclone sync <source> <remote>:<path> --dry-run
```

## Rclone - Move Files

Move files from source to destination.

```
rclone move <source> <remote>:<path> --progress
```

## Rclone - Bidirectional Sync

Sync changes in both directions. The first run requires `--resync`.

```
rclone bisync <path1> <remote>:<path2> --resync
```

## Rclone - Check Differences

Compare source and destination and report files that differ.

```
rclone check <source> <remote>:<path>
```

## Rclone - Get Size

Show the total size and object count of a remote path.

```
rclone size <remote>:<path>
```

## Rclone - Disk Usage Browser

Explore remote usage interactively (ncdu-style).

```
rclone ncdu <remote>:<path>
```

## Rclone - Make Directory

Create a directory or bucket on the remote.

```
rclone mkdir <remote>:<path>
```

## Rclone - Delete Files

Remove the files in a path, leaving directories in place.

```
rclone delete <remote>:<path>
```

## Rclone - Purge Path

Remove a path and all of its contents.

```
rclone purge <remote>:<path>
```

## Rclone - Remove Duplicates

Interactively find and remove duplicate files.

```
rclone dedupe <remote>:<path>
```

## Rclone - Mount a Remote

Mount a remote as a local filesystem.

```
rclone mount <remote>:<path> <mount-point> --vfs-cache-mode writes
```

## Rclone - Serve over HTTP

Serve a remote path over HTTP.

```
rclone serve http <remote>:<path> --addr :8080
```

## Rclone - Filter Files

Only transfer files matching include patterns.

```
rclone copy <source> <remote>:<path> --include "*.{jpg,png}"
```

## Rclone - Limit Bandwidth

Cap transfer speed.

```
rclone sync <source> <remote>:<path> --bwlimit 10M
```

## Rclone - Encrypt Config

Set a password to encrypt the configuration file.

```
rclone config encryption set
```
