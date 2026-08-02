# restic

restic backs up files into an encrypted, deduplicated, content-addressed repository, producing immutable snapshots that can be listed, mounted and restored individually. On a Linux fleet it replaces hand-rolled tar-and-rotate scripts, because a repeat backup only stores blocks it has never seen before and every snapshot stays a complete, browsable view of the tree.

#platform/multiple #target/Linux #cat/Backup

% restic, backup, snapshots, deduplication, restore, encryption, prune, forget, retention, repository, sftp, rest server, s3, minio, fuse, mount, offsite

## restic - Check the Version Before Trusting a Flag

restic gains and renames commands between releases, and an on-premise host installed from a distribution package is often several versions behind upstream. Check first, because a flag documented for the current release may simply not exist on the box in front of you.

```
restic version
```

This cheatsheet is written against restic 0.19.1. The differences that bite most often on older hosts: `--insecure-no-password` and the `restore` flags `--dry-run`, `--overwrite` and `--delete` arrived in 0.17.0; exit codes 10 and 11 arrived in 0.17.0 and 12 in 0.17.1; `rebuild-index` is now a deprecated alias for `repair index`; and `prune --repack-small` is deprecated in favour of `--repack-smaller-than`.

Ubuntu and Debian ship restic in the archive, but the packaged version lags upstream. Compare the two before writing a script that has to run on every host:

```
restic version && apt-cache policy restic
```

## restic - Initialise a Local or Removable-Disk Repository

`init` creates the repository structure and the first key. A local path is the simplest backend and the right one for a directly attached backup disk or an NFS/CIFS mount.

```
restic init --repo /srv/restic-repo
```

The repository is a plain directory tree of encrypted pack files. It has no filesystem requirements beyond ordinary read/write, so a mounted share works, but note that restic locks the repository with files inside it — two hosts writing to the same repository over NFS at the same time is safe by design, while a share that does not honour renames is not.

Since 0.17.0 a repository can be created without encryption password, which you should only do when the storage itself is already encrypted and access-controlled. The flag must then be passed to every later command:

```
restic init --repo /srv/restic-repo --insecure-no-password
```

## restic - Initialise a Repository over SFTP

The `sftp:` backend needs nothing on the far side but an SSH account — no restic binary, no daemon. That makes it the lowest-friction on-premise remote target.

```
restic -r sftp:user@host:/srv/restic-repo init
```

A path without a leading slash is relative to the remote user's home directory; the double slash form is how you write an absolute path when using the URL syntax with a port:

```
restic -r sftp://user@host:2222//srv/restic-repo init
```

restic shells out to `ssh`, so anything in `~/.ssh/config` applies and a host alias collapses the command. Define the alias with its key, port and `BatchMode yes`, and unattended jobs stop depending on the environment:

```
restic -r sftp:restic-backup-host:/srv/restic-repo init
```

Override the transport explicitly when there is no usable ssh config, for example inside a container. `-o sftp.command` replaces the whole command restic runs:

```
restic -r sftp:user@host:/srv/restic-repo -o sftp.command="ssh -i /root/.ssh/id_ed25519_backup -o BatchMode=yes user@host -s sftp" init
```

SFTP gives the backup account write access to the whole repository, which means a compromised production host can also delete its own backups. That is the main reason to prefer the REST server below.

## restic - Initialise a Repository on a REST Server

`rest-server` is restic's own small HTTP service. It is the best on-premise target because it supports **append-only mode**: clients can write new data and read it back, but cannot delete anything. A ransomware event on a production host then cannot destroy the archive.

```
restic -r rest:http://host:8000/ init
```

Use a per-host subpath so each client gets its own repository, and put TLS in front of it. Credentials can be embedded in the URL, though that leaks them into the process list:

```
restic -r rest:https://user:pass@host:8000/my_backup_repo/ init
```

Keep the HTTP credentials out of the command line by passing them in the environment instead:

```
export RESTIC_REST_USERNAME=<rest-user>
export RESTIC_REST_PASSWORD=<rest-password>
restic -r rest:https://host:8000/my_backup_repo/ init
```

A unix socket avoids the network entirely when restic and the server run on the same machine:

```
restic -r rest:http+unix:///tmp/rest.socket:/my_backup_repo/ init
```

Note that with append-only enabled, `forget` and `prune` will fail from the client. Retention has to be run on the server side, where the append-only restriction does not apply.

## restic - Initialise a Repository on S3-Compatible Storage

The `s3:` backend talks to MinIO, Ceph RGW and any other S3-compatible object store as well as to AWS. Credentials come from the standard AWS environment variables.

```
export AWS_ACCESS_KEY_ID=<access-key>
export AWS_SECRET_ACCESS_KEY=<secret-key>
restic -r s3:http://localhost:9000/restic init
```

An on-premise MinIO reached over TLS, using an explicit scheme, host, port and bucket:

```
restic -r s3:https://minio.internal:9000/backups init
```

A path after the bucket name puts the repository in a prefix, so one bucket can hold several repositories:

```
restic -r s3:https://minio.internal:9000/backups/web1 init
```

Object storage is where object-lock and versioning policies live, which gives you immutability without the REST server. Set the region when the endpoint does not imply one, since a wrong region shows up as an opaque authentication failure:

```
restic -o s3.region=us-east-1 -r s3:https://minio.internal:9000/backups init
```

## restic - Supply the Repository and Password Without Interaction

Every restic command needs a repository and a password. Passing them through the environment is what makes restic scriptable, and putting the password in a file rather than in `RESTIC_PASSWORD` keeps it out of `/proc/<pid>/environ` and out of the shell history.

```
export RESTIC_REPOSITORY=rest:https://backup.internal:8000/web1/
export RESTIC_PASSWORD_FILE=/etc/restic/web1.pass
restic snapshots
```

The equivalent flags, for when a single command needs a different repository than the environment specifies. `-r`/`--repo` and `-p`/`--password-file` are the short forms:

```
restic -r /srv/restic-repo -p /etc/restic/local.pass snapshots
```

`--repository-file` (or `RESTIC_REPOSITORY_FILE`) reads the repository location from a file, which is convenient when the URL contains credentials that should not sit in a unit file:

```
restic --repository-file /etc/restic/repo --password-file /etc/restic/web1.pass snapshots
```

`--password-command` runs a shell command and uses its standard output as the password. This is the hook for a secrets manager, so the password never lands on disk at all:

```
restic --password-command "vault kv get -field=password secret/restic/web1" snapshots
```

Whichever you choose, the credential files must be root-owned and mode 600. A readable password file next to a readable repository is the same as no encryption:

```
install -o root -g root -m 600 /dev/null /etc/restic/web1.pass
```

## restic - Take a Backup

`backup` walks the given paths, chunks their contents, stores only chunks the repository has never seen, and writes a snapshot. Several paths in one command produce one snapshot covering all of them.

```
restic backup /etc /srv /home
```

Tags label a snapshot so retention and restores can select it later. Use them to separate concerns that share a repository, such as filesystem backups and database dumps:

```
restic backup --tag daily --tag system /etc /srv
```

`--host` overrides the hostname recorded in the snapshot. Set it explicitly for anything that moves between machines — a container, a VM that gets rebuilt, or a job that backs up a network share — otherwise a rename silently starts a new snapshot lineage and breaks both deduplication against the parent and the retention grouping.

```
restic backup --host web1 --tag daily /srv/app
```

`--one-file-system` (`-x`) stops the walk at filesystem boundaries. Without it a backup of `/` descends into `/proc`, `/sys`, `/dev` and every bind mount and NFS share:

```
restic backup --one-file-system --exclude-caches /
```

`--dry-run` (`-n`) reports what would be stored without writing anything. Combine it with `-v` when adding a new path to an established job:

```
restic backup --dry-run -v /srv/newapp
```

`--files-from` reads the list of paths to back up from a file, one per line, which pairs well with a generated manifest. `--files-from-verbatim` is the variant that does no globbing or whitespace stripping, so it is the safe one for paths containing spaces or `*`:

```
restic backup --files-from /etc/restic/paths.txt --tag daily
```

## restic - Exclude Paths from a Backup

`--exclude` takes a pattern; a pattern with no slash matches at any depth, one with a slash is matched against the whole path. Repeat the flag for each rule.

```
restic backup /srv --exclude="*.tmp" --exclude="/srv/cache"
```

`--iexclude` is the same thing with case-insensitive matching, which matters on filesystems restored from Windows or on case-insensitive mounts:

```
restic backup /srv --iexclude="*.ISO"
```

`--exclude-file` keeps a long rule set in version control instead of in the unit file. One pattern per line, `#` starts a comment, and the flag can be given more than once:

```
restic backup /srv --exclude-file=/etc/restic/excludes.txt --exclude-file=/etc/restic/excludes.local.txt
```

`--exclude-caches` skips the contents of any directory containing a `CACHEDIR.TAG` file, per the Cache Directory Tagging Standard. It is close to free and it removes a surprising amount of junk on a developer or build host:

```
restic backup /home --exclude-caches
```

`--exclude-if-present` generalises that to a marker file of your own choosing, so application owners can opt a directory out without touching the backup config:

```
restic backup /srv --exclude-if-present .nobackup
```

`--exclude-larger-than` caps the file size, which is how you keep a stray VM image or core dump out of a job that is otherwise all small files:

```
restic backup /srv --exclude-larger-than 1G
```

## restic - Back Up a Database Dump from Standard Input

`--stdin` stores whatever arrives on standard input as a single file in a snapshot. This avoids writing a multi-gigabyte dump to disk first, which on a production database server is often the scarcest resource.

```
mysqldump --single-transaction --all-databases | restic backup --stdin --stdin-filename all-databases.sql --tag mysql
```

`--stdin-filename` sets the name the data is stored under; without it the file is called `stdin`, which makes later `restore --include` and `dump` calls awkward. The PostgreSQL equivalent:

```
pg_dumpall | restic backup --stdin --stdin-filename pgdump.sql --tag postgres --host db1
```

The important caveat is pipeline error handling: if the dump command fails halfway, restic still stores the truncated output as a perfectly valid snapshot. `--stdin-from-command` fixes this by having restic run the command itself, so a non-zero exit status from the dump aborts the backup instead of committing a broken one:

```
restic backup --stdin-from-command --stdin-filename pgdump.sql -- pg_dumpall -U postgres
```

If you must keep the pipe form, set `set -o pipefail` and check the exit status yourself, because otherwise a failed `mysqldump` produces a successful restic run over an empty stream. Streamed data also deduplicates worse than a file tree, since a small change early in a dump shifts every subsequent chunk boundary — and do not pre-compress it, because restic compresses on its own and a gzip stream deduplicates against nothing.

## restic - List Snapshots

`snapshots` prints the snapshot ID, time, host, tags and paths. The ID is what every other command takes, and its short form is enough as long as it is unambiguous.

```
restic snapshots
```

Filter by tag, host or path when one repository holds several jobs. Multiple tags in one `--tag` value are an AND; repeating `--tag` is an OR:

```
restic snapshots --tag daily --host web1
```

`--group-by` controls how snapshots are grouped in the output; the default is host and paths. Grouping by tags as well makes a shared repository readable, and — more importantly — it is the same grouping that `forget` applies:

```
restic snapshots --group-by host,paths,tags
```

`--latest n` shows only the newest `n` snapshots per group, which is the quick "did last night's run happen" check:

```
restic snapshots --latest 1 --host web1
```

`--compact` drops the paths column for a one-line-per-snapshot listing on a wide fleet:

```
restic snapshots --compact --group-by host
```

## restic - Look Inside a Snapshot Without Restoring

`ls` lists the files in a snapshot. `latest` is a valid snapshot ID meaning the newest snapshot matching the filters, so most interactive commands never need a real ID.

```
restic ls latest /etc
```

`--long` adds mode, owner, size and time, and `--recursive` descends the whole tree rather than one directory level:

```
restic ls --long --recursive latest /etc/nginx
```

`find` searches for a path pattern across snapshots, and tells you which snapshots contain it. This is how you answer "when did this file last exist" before restoring anything:

```
restic find "*.conf" --host web1
```

Narrow it to a time window and a single snapshot, and use `-i` for a case-insensitive match:

```
restic find --oldest 2026-01-01 --newest "2026-06-30 23:59:59" -i "nginx.conf"
```

`cat` prints restic's internal objects — the repository config, a snapshot's JSON metadata, a key. Use it when debugging the repository itself rather than the data in it:

```
restic cat snapshot latest
```

## restic - Compare Two Snapshots

`diff` reports what changed between two snapshots: added, removed, modified, and the size delta. Answering "what did that deploy actually touch" costs nothing, because it compares metadata rather than reading data.

```
restic diff 073a90db 4e5d5487
```

`--metadata` includes permission, ownership and timestamp changes, which are invisible in the default output but are exactly what breaks an application after a bad `chown -R`:

```
restic diff --metadata 073a90db latest
```

## restic - Restore a Snapshot

`restore` writes a snapshot's contents into `--target`. The target directory is created if missing, and the snapshot's absolute paths are recreated underneath it — restoring `/etc` with `--target /tmp/restore` produces `/tmp/restore/etc`.

```
restic restore latest --target /tmp/restore
```

Restore a specific snapshot by ID rather than the latest, which is what you want when the latest snapshot already contains the corruption you are recovering from:

```
restic restore 79766175 --target /tmp/restore
```

`--include` restricts the restore to matching paths, so a single file does not require unpacking the whole tree. `--exclude`, `--iinclude` and `--iexclude` work the same way:

```
restic restore latest --target /tmp/restore --include /srv/app/config
```

Restore a subfolder directly with the `snapshotID:path` syntax, which strips the leading path components instead of recreating them under the target:

```
restic restore 79766175:/srv/app --target /srv/app
```

`--verify` re-reads every restored file and checks its content hash after writing. It doubles the I/O, and it is worth it for a disaster recovery where you must be able to state that the restore is correct:

```
restic restore latest --target /tmp/restore --verify
```

`--dry-run` with `-vv` lists exactly what would be written. Do this before any restore that targets a live path rather than a scratch directory — `--overwrite always` is the default, so a careless restore will clobber current files:

```
restic restore latest --target /srv/app --dry-run -vv
```

`--overwrite if-newer` leaves destination files alone unless the snapshot's copy is newer, and `--delete` removes files in the target that the snapshot does not contain, turning the restore into an exact mirror. `--delete` is destructive; always dry-run it first:

```
restic restore latest --target /srv/app --overwrite if-newer --delete --dry-run -vv
```

## restic - Extract a Single File Without Restoring

`dump` writes one file from a snapshot to standard output. For the common "someone deleted one config" case this is faster and less disruptive than a restore, because nothing is written to disk unless you redirect it.

```
restic dump latest /etc/nginx/nginx.conf
```

Feed a database dump straight back into the server without staging it, which matters when the dump is larger than the free space:

```
restic dump latest /pgdump.sql | psql -U postgres
```

`dump` also serialises a whole directory as an archive, `-a tar` by default or `-a zip`. This is the way to hand a subtree to someone who has no access to the repository:

```
restic dump -a zip latest /srv/app/config > /tmp/config.zip
```

## restic - Mount the Repository over FUSE

`mount` exposes every snapshot as a read-only directory tree. This is usually the fastest route to recovering a handful of files, because you can browse, `diff` and `cp` with ordinary tools instead of guessing at include patterns.

```
restic mount /mnt/restic
```

The default layout gives four views of the same snapshots: `ids/<id>`, `snapshots/<time>`, `hosts/<host>/<time>` and `tags/<tag>/<time>`. Wherever a directory is keyed by time, restic also generates a `latest` symlink, so normal shell tooling finds the file for you:

```
ls /mnt/restic/hosts/web1/latest/etc/nginx/
```

Copy out of the mount with `rsync --hard-links`, because restic's FUSE layer represents deduplicated identical files as hardlinks and a plain copy would expand them:

```
rsync -a --hard-links /mnt/restic/hosts/web1/latest/srv/app/ /srv/app/
```

The mount is single-process and blocks until interrupted, so run it in a second terminal or under `systemd-run`. It needs the `fuse` kernel module and `fusermount` in `PATH`, which rules it out on a minimal container image, and the mountpoint must not sit inside a local repository directory. Unmount with:

```
fusermount -u /mnt/restic
```

## restic - Forget Snapshots with a Retention Policy

`forget` applies a retention policy and removes the snapshot references that fall outside it. **It does not free any disk space** — it only unlinks snapshots from the repository. Space is reclaimed by `prune`, covered in the next section, and that separation is the single most important thing to understand about restic's retention model.

```
restic forget --keep-daily 7 --keep-weekly 5 --keep-monthly 12 --keep-yearly 3
```

**Always run it with `--dry-run` (`-n`) first.** `forget` is the destructive half of restic and a wrong policy is not recoverable — once the snapshots are gone and a `prune` has run, the data is gone. Read the "remove" list in the output before running it for real:

```
restic forget --keep-daily 7 --keep-weekly 5 --keep-monthly 12 --dry-run
```

The policy flags count *snapshots per period*, not days: `--keep-daily 7` keeps the most recent snapshot from each of the last seven days that have any snapshot, so a host that was offline for a month still keeps seven dailies. `--keep-last n` keeps the newest `n` regardless of time, and is worth adding as a floor under any time-based policy:

```
restic forget --keep-last 3 --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --keep-yearly 2 --dry-run
```

`--keep-within <duration>` keeps everything newer than a duration relative to the *latest* snapshot, not to now. The `--keep-within-daily`, `--keep-within-weekly`, `--keep-within-monthly` and `--keep-within-yearly` variants apply a period rule only inside that window:

```
restic forget --keep-within 14d --keep-within-monthly 1y --dry-run
```

`--keep-tag` protects any snapshot carrying a tag list, regardless of age. Tag the pre-upgrade or year-end snapshots and no policy will ever remove them:

```
restic forget --keep-daily 7 --keep-tag keep --keep-tag release --dry-run
```

Policies apply **per group**, and the default grouping is host and paths. Filter and group deliberately when one repository serves several jobs, otherwise a policy meant for the filesystem backups also thins the database dumps:

```
restic forget --host web1 --tag daily --group-by host,paths,tags --keep-daily 14 --dry-run
```

Two traps worth memorising. On `forget`, `-H` is the shorthand for `--keep-hourly`, not for `--host` as it is on every other command — spell out `--host`. And `--hostname` still exists but is deprecated in favour of `--host`:

```
restic forget --host db1 --keep-daily 30 --dry-run
```

A group with no matching keep rule would be emptied entirely; restic refuses that unless you pass `--unsafe-allow-remove-all`. Treat a run that asks for that flag as a policy bug, not as something to force:

```
restic forget --tag decommissioned --unsafe-allow-remove-all --dry-run
```

## restic - Prune to Reclaim Disk Space

`prune` is what actually deletes data. It finds blobs no remaining snapshot references, repacks the pack files that are partly still in use, and removes the rest. Until it runs, a forgotten snapshot's data still occupies the disk.

```
restic prune
```

`--dry-run` (`-n`) reports how much would be removed and repacked without touching anything, which is how you size the maintenance window before a first prune on a long-neglected repository:

```
restic prune --dry-run -v
```

Chain it onto `forget` with `--prune`, which runs `prune` only if snapshots were actually removed. This is the normal shape of a nightly retention job, and the one place where skipping the dry run is acceptable — because the policy was validated when it was written:

```
restic forget --host web1 --keep-daily 7 --keep-weekly 5 --keep-monthly 12 --prune
```

`--max-unused` sets how much unreferenced data restic tolerates rather than repacking, defaulting to 5%. Raising it makes prune much cheaper in I/O at the cost of disk; `--max-unused 0` reclaims everything and rewrites the most:

```
restic prune --max-unused 20%
```

`--max-repack-size` caps the volume rewritten in one run, so a prune on a large remote repository can be spread over several nights instead of saturating the link:

```
restic prune --max-repack-size 50G
```

`--repack-cacheable-only` restricts repacking to metadata packs, which are small and locally cached — a cheap way to keep the index tidy without moving bulk data. `--repack-smaller-than` consolidates small pack files, which is what fixes a repository that has accumulated millions of tiny objects:

```
restic prune --repack-smaller-than 16M
```

Note the deprecation: older material recommends `--repack-small`, which is deprecated in favour of `--repack-smaller-than`. Prune takes an exclusive lock and is the one operation that must not be interrupted casually, so run it outside the backup window rather than in parallel with it:

```
restic prune --repack-cacheable-only
```

## restic - Check Repository Integrity

`check` verifies the repository's structure: that the index matches the pack files and that every blob a snapshot references exists. It reads metadata only, so it is fast, and it catches the failure mode that matters — a repository that has silently stopped being restorable.

```
restic check
```

Structural checks do not read the data itself. `--read-data` downloads and verifies every pack, which is the only test that proves the bytes are still good, and it costs a full read of the repository:

```
restic check --read-data
```

`--read-data-subset` verifies a random fraction instead, so a scheduled job can cover the whole repository over time without ever doing a full read. A percentage, a size, or an `n/t` form that walks deterministically through `t` parts:

```
restic check --read-data-subset=10%
```

Use the `n/t` form driven by the day of the month to check one twentieth of the data each night, covering everything over about three weeks:

```
restic check --read-data-subset=$(date +%d)/20
```

`--with-cache` reuses the existing local cache rather than a fresh temporary one, which makes a routine check much faster at the cost of not re-verifying cached metadata:

```
restic check --with-cache
```

Schedule `check` separately from `backup`. An untested backup is a guess, and restic's design — deduplicated blobs shared across every snapshot — means a single corrupt pack can affect every snapshot that references it, so the earlier it is found the more likely an older copy still exists elsewhere.

```
restic check --read-data-subset=5% || echo "restic check FAILED" | mail -s "backup integrity" ops@example.com
```

## restic - Report Repository and Snapshot Size

`stats` answers two different questions depending on `--mode`, and confusing them is why restic's sizes look wrong at first glance. The default `restore-size` reports the total size a restore would produce, counting shared data once per snapshot.

```
restic stats latest
```

`--mode raw-data` reports the actual size of the data stored in the repository after deduplication and compression. This is the number to compare against disk usage and the one to trend over time:

```
restic stats --mode raw-data
```

Run it over all snapshots to see the whole repository, and over one snapshot to see what a restore of it would cost in disk:

```
restic stats --mode restore-size --host web1 --tag daily
```

`--mode files-by-contents` counts distinct file contents rather than paths, which quantifies how much of the tree is duplicate files. `--mode blobs-per-file` exposes chunking behaviour and is mostly a debugging tool:

```
restic stats --mode files-by-contents latest
```

## restic - Unlock and Repair a Damaged Repository

restic locks the repository during write operations. A killed process or a lost network connection leaves a stale lock behind, and the next run fails with exit code 11 rather than risking concurrent modification.

```
restic unlock
```

`unlock` removes only locks restic considers stale. `--remove-all` removes every lock including live ones, so run it only after confirming no restic process is actually running anywhere against that repository:

```
restic unlock --remove-all
```

`repair index` rebuilds the index from the pack files themselves. This is the fix when `check` reports index errors, and it is safe: the index is derived data and can always be regenerated.

```
restic repair index
```

`--read-all-packs` rebuilds from scratch by reading every pack rather than trusting existing index entries, which is slower and is what you use when the index is badly damaged:

```
restic repair index --read-all-packs
```

Older restic releases called this command `rebuild-index`. The old name still exists as a deprecated alias, so a script that has to run across mixed versions can keep using it, but new work should say `repair index`:

```
restic rebuild-index
```

`repair snapshots` rewrites snapshots that reference missing data, dropping the unreadable files so the rest of the snapshot becomes restorable again. It creates new snapshots and leaves the originals unless `--forget` is given, and it should always be dry-run first:

```
restic repair snapshots --dry-run
```

`repair packs` salvages the readable blobs from damaged pack files identified by `check`. Both repair subcommands are last-resort tools — reach for them after `check` has told you exactly what is broken, not speculatively:

```
restic repair packs <packID>
```

## restic - Manage Repository Keys

A repository can hold several keys, each a password that unlocks the same data. Give every host its own key so a compromised or decommissioned server can be cut off without re-encrypting the archive or changing anyone else's password.

```
restic key list
```

`key add` creates a new key after authenticating with an existing one. The currently used key is marked with an asterisk in `key list`:

```
restic key add
```

`key remove` deletes a key by ID, which is the revocation step when a host is retired. Removing the key you are currently authenticated with is refused:

```
restic key remove <keyID>
```

`key passwd` changes the current password: it adds a new key and removes the old one, returning a new key ID. Because the data encryption key is unchanged, this is instantaneous regardless of repository size:

```
restic key passwd
```

Losing every key means losing the repository — there is no recovery path, by design. Back the passwords up somewhere that does not depend on the systems being backed up.

```
restic key list --json
```

## restic - Copy Snapshots to an Offsite Repository

`copy` replicates snapshots from one repository into another. This is how you get a second, offsite copy without re-reading the source filesystems, and the destination can use a different password and a different backend.

```
restic copy --from-repo /srv/restic-repo --from-password-file /etc/restic/local.pass
```

The source repository is addressed with the `--from-*` flags — `--from-repo`, `--from-repository-file`, `--from-password-file`, `--from-password-command`, `--from-key-hint` — while the plain `-r`/`--repo` flags address the destination. The corresponding `RESTIC_FROM_*` environment variables exist for all of them.

```
restic -r s3:https://minio.dr-site:9000/backups copy --from-repo /srv/restic-repo --host web1 --tag daily
```

Copy specific snapshots rather than everything, which is how you seed a new offsite repository incrementally:

```
restic copy --from-repo /srv/restic-repo 410b18a2 4e5d5487 latest
```

Two properties to plan around. `copy` decrypts and re-encrypts, so it reads and writes the full snapshot content rather than moving pack files — bandwidth cost is real. And it does not re-chunk, so unless the destination was created with matching chunker parameters, copied files may occupy up to twice their space. Initialise the destination from the source to avoid that:

```
restic init --repo s3:https://minio.dr-site:9000/backups --from-repo /srv/restic-repo --copy-chunker-params
```

## restic - Control the Local Cache

restic keeps a metadata cache under `~/.cache/restic` (or `$XDG_CACHE_HOME/restic`). It exists so that operations like `snapshots`, `ls` and the parent-snapshot lookup during a backup do not re-download the index from a remote repository every time.

```
restic cache
```

Root-run systemd jobs and interactive users have different `HOME` values and therefore different caches, which is the usual reason a scripted backup is unexpectedly slow. Pin the location explicitly for anything unattended:

```
restic --cache-dir /var/cache/restic backup /srv
```

`--no-cache` disables it entirely. Correctness is unaffected — the cache is purely ephemeral — but every metadata read goes to the repository, so use it only on a host with no writable disk or where the cache would leak metadata:

```
restic --no-cache snapshots
```

Old per-repository cache directories accumulate as repositories come and go. `cache --cleanup` removes those older than `--max-age` days, defaulting to 30:

```
restic cache --cleanup --max-age 7
```

The global `--cleanup-cache` flag does the same tidy-up as a side effect of a normal command, which is convenient to add to a weekly maintenance run:

```
restic --cleanup-cache check
```

## restic - Produce Machine-Readable Output

`--json` switches output to JSON for the commands that support it, which as of 0.19.1 are `backup`, `cat`, `check`, `diff`, `find`, `forget`, `init`, `key list`, `ls`, `restore`, `snapshots`, `stats`, `tag` and `version`. This is the interface to use for monitoring rather than parsing human output that changes between releases.

```
restic snapshots --json | jq -r '.[] | [.short_id, .time, .hostname, (.tags // [] | join(","))] | @tsv'
```

Long-running commands emit JSON lines — one JSON object per line, each with a `message_type` field — rather than a single document. A backup emits `status` messages throughout and exactly one `summary` at the end, which is the object worth recording:

```
restic backup /srv --json | jq -c 'select(.message_type == "summary")'
```

Extract the numbers a monitoring system actually needs from that summary: how much new data was stored and how long the run took.

```
restic backup /srv --json | jq -r 'select(.message_type=="summary") | "added=\(.data_added) files_new=\(.files_new) duration=\(.total_duration)"'
```

Check the age of the newest snapshot, which is the alert that matters — a backup job that stopped running is far more common than one that fails loudly:

```
restic snapshots --latest 1 --host web1 --json | jq -r '.[0].time'
```

## restic - Check Exit Codes in Scripts

restic's exit status distinguishes "the source data had a problem" from "the repository was unreachable", which lets a wrapper decide between retrying, alerting and paging.

```
restic backup /srv; echo "rc=$?"
```

The documented values are `0` success, `1` command failed, `2` Go runtime error, `3` backup could not read some source data or forget could not remove one or more snapshots, `10` repository does not exist, `11` failed to lock the repository, `12` wrong password, and `130` cancelled by SIGINT or SIGTERM. Codes 10 and 11 exist since 0.17.0 and 12 since 0.17.1; on older releases those conditions all return 1.

```
restic snapshots >/dev/null 2>&1; echo "rc=$?"
```

Code 3 is the one that needs judgement. The snapshot **was** created and is usable; some files could not be read, typically because of permissions or because they vanished mid-run. Treat it as a warning on a live filesystem, not as a failure:

```
restic backup /srv; rc=$?; [ "$rc" -eq 0 ] || [ "$rc" -eq 3 ] || exit "$rc"
```

Code 11 means a stale or live lock, and it is the right trigger for an automatic retry rather than an alert. `--retry-lock` makes restic wait for the lock itself instead of failing immediately:

```
restic --retry-lock 15m forget --keep-daily 7 --prune
```

## restic - Run Backups from a systemd Timer

A systemd service plus timer is the right scheduler on a modern Linux host: it gives you `Persistent=true` so a missed run fires after a reboot, journal capture of restic's output, and `OnFailure=` for alerting — none of which cron provides. See the `systemctl` cheatsheet for managing units and timers themselves.

```
systemctl list-timers restic-backup.timer
```

Point the unit at an `EnvironmentFile` holding `RESTIC_REPOSITORY` and `RESTIC_PASSWORD_FILE` so no secret appears in the unit or in the process list, and run backup and retention as separate `ExecStart=` lines so a failing prune does not mask a failing backup:

```
systemd-analyze cat-config systemd/system/restic-backup.service
```

Check the last run and its exit status without leaving the terminal, which is the fastest triage after an alert:

```
systemctl status restic-backup.service && journalctl -u restic-backup.service -n 50 --no-pager
```

Run the job immediately to test it, exactly as the timer would, rather than pasting the command by hand — that is what catches a wrong `HOME`, a missing `PATH` entry or an unreadable password file:

```
systemctl start restic-backup.service
```

Split the schedule: back up often, forget and prune daily, and check weekly. Prune takes an exclusive lock, so it must not overlap the backup timer.

```
systemctl list-timers 'restic-*'
```
