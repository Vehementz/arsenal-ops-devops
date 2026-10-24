# Borg

BorgBackup is a deduplicating backup program with optional compression and authenticated encryption. It supports local and remote (SSH) repositories.

#platform/multiple #target/Backup #cat/DevOps

% borg, borgbackup, backup, deduplication, encryption

## Borg - Check Installation

Verify that Borg has been installed correctly.

```
borg --version
```

## Borg - Initialize a Repository

Create a new encrypted repository.

```
borg init --encryption=repokey <repo-path>
```

Initialize a repository on a remote host over SSH.

```
borg init --encryption=repokey ssh://<user>@<host>/<path-to-repo>
```

## Borg - Create a Backup

Create a new archive named after the host and current timestamp, with stats and progress.

```
borg create --stats --progress <repo-path>::'{hostname}-{now}' <path-to-backup>
```

## Borg - Create a Compressed Backup with Exclusions

Create an archive using zstd compression while excluding patterns.

```
borg create --stats --compression zstd,6 --exclude '<pattern>' <repo-path>::<archive-name> <path-to-backup>
```

## Borg - List Archives

List all archives in a repository.

```
borg list <repo-path>
```

## Borg - List Archive Contents

List the files contained in a given archive.

```
borg list <repo-path>::<archive-name>
```

## Borg - Show Archive Info

Show details and size statistics about an archive or repository.

```
borg info <repo-path>::<archive-name>
```

## Borg - Compare Archives

Show the differences between two archives.

```
borg diff <repo-path>::<archive-1> <archive-2>
```

## Borg - Extract an Archive

Restore the contents of an archive into the current directory.

```
borg extract <repo-path>::<archive-name>
```

Restore only specific paths, previewing first with a dry run.

```
borg extract --dry-run --list <repo-path>::<archive-name> <path>
```

## Borg - Mount an Archive

Mount an archive as a FUSE filesystem to browse and copy files.

```
borg mount <repo-path>::<archive-name> <mount-point>
```

Unmount it when done.

```
borg umount <mount-point>
```

## Borg - Export a Tar Archive

Export an archive as a compressed tarball.

```
borg export-tar <repo-path>::<archive-name> <output>.tar.gz
```

## Borg - Delete an Archive

Delete a single archive from a repository.

```
borg delete <repo-path>::<archive-name>
```

## Borg - Prune Old Archives

Keep a defined number of daily, weekly and monthly archives and remove the rest. Use `--dry-run` first.

```
borg prune --list --dry-run --keep-daily 7 --keep-weekly 4 --keep-monthly 6 <repo-path>
```

## Borg - Compact Repository

Free space in the repository after deleting or pruning archives (Borg 1.2+).

```
borg compact <repo-path>
```

## Borg - Check Repository Integrity

Verify the consistency of a repository and its archives.

```
borg check --verbose <repo-path>
```

## Borg - Export Key

Back up the repository key; required to restore when using `repokey` or `keyfile` encryption.

```
borg key export <repo-path> <key-backup-file>
```

## Borg - Set Passphrase via Environment

Provide the passphrase non-interactively, for example in scripts or cron jobs.

```
export BORG_PASSPHRASE='<passphrase>'
```
