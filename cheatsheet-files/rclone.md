# Rclone

Rclone is a command-line program to manage files on cloud storage. It syncs, copies, mounts and inspects files across more than 70 storage providers (S3, GCS, Azure, Drive, SFTP, ...).

#platform/multiple #target/Storage #cat/DevOps

% rclone, cloud storage, sync, backup, s3, copy

## Rclone - Check Installation

Verify that Rclone has been installed correctly.

```
rclone version
```

## Rclone - Configure a Remote

Interactively create, edit or delete a remote.

```
rclone config
```

## Rclone - List Remotes

List the remotes defined in the configuration file.

```
rclone listremotes
```

## Rclone - Show Config File Path

Show where the configuration file is stored.

```
rclone config file
```

## Rclone - List Directories

List top-level directories of a remote path.

```
rclone lsd <remote>:<path>
```

## Rclone - List Files

List all objects in a path with size and path.

```
rclone ls <remote>:<path>
```

## Rclone - List Files with Details

List objects with modification time, size and path.

```
rclone lsl <remote>:<path>
```

## Rclone - Show Size of a Path

Show total size and number of objects.

```
rclone size <remote>:<path>
```

## Rclone - Show Directory Tree

Display a remote path as a tree.

```
rclone tree <remote>:<path>
```

## Rclone - Copy Files

Copy files from source to destination, skipping identical files. Does not delete anything on the destination.

```
rclone copy <source> <remote>:<destination> --progress
```

## Rclone - Sync Files

Make the destination identical to the source. Files only present on the destination are deleted.

```
rclone sync <source> <remote>:<destination> --progress
```

## Rclone - Sync Dry Run

Preview what a sync would do without changing anything.

```
rclone sync <source> <remote>:<destination> --dry-run
```

## Rclone - Move Files

Move files from source to destination, deleting them from the source after transfer.

```
rclone move <source> <remote>:<destination> --progress
```

## Rclone - Bidirectional Sync

Sync changes in both directions. The first run requires `--resync`.

```
rclone bisync <path1> <remote>:<path2> --resync
```

## Rclone - Check Files Match

Compare source and destination and report differences.

```
rclone check <source> <remote>:<destination>
```

## Rclone - Delete Files

Remove the files in a path, leaving directories in place.

```
rclone delete <remote>:<path>
```

## Rclone - Remove Path and Contents

Remove a path and all of its contents.

```
rclone purge <remote>:<path>
```

## Rclone - Make Directory

Create a directory or bucket on a remote.

```
rclone mkdir <remote>:<path>
```

## Rclone - Print File Contents

Print the contents of a remote file to stdout.

```
rclone cat <remote>:<path/to/file>
```

## Rclone - Mount a Remote

Mount a remote as a local filesystem using FUSE.

```
rclone mount <remote>:<path> <mountpoint> --vfs-cache-mode full
```

## Rclone - Serve a Remote over HTTP

Serve a remote path over HTTP.

```
rclone serve http <remote>:<path> --addr :8080
```

## Rclone - Filter Files

Include or exclude files by pattern when transferring.

```
rclone copy <source> <remote>:<destination> --include "*.jpg" --exclude "tmp/**"
```

## Rclone - Limit Bandwidth

Throttle transfer speed.

```
rclone copy <source> <remote>:<destination> --bwlimit 10M
```

## Rclone - Speed Up Transfers

Increase parallel transfers and checkers.

```
rclone copy <source> <remote>:<destination> --transfers 16 --checkers 32 --progress
```

## Rclone - Encrypt a Remote Path

After creating a `crypt` remote with `rclone config`, copy files into it to store them encrypted.

```
rclone copy <source> <crypt-remote>:<path>
```

## Rclone - Show Remote Free Space

Show total, used and free space of a remote.

```
rclone about <remote>:
```

## Rclone - Generate Public Link

Generate a public link to a file or folder, if the provider supports it.

```
rclone link <remote>:<path>
```

## Rclone - Remove Duplicates

Find and resolve duplicate files interactively.

```
rclone dedupe <remote>:<path>
```

## Rclone - Debug Logging

Run a command with verbose debug logs written to a file.

```
rclone sync <source> <remote>:<destination> -vv --log-file=rclone.log
```
