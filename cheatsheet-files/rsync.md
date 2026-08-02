# rsync

rsync copies and synchronises files and directory trees, transferring only the differences between source and destination using its delta-transfer algorithm. On a server fleet it is the default tool for deployments, backups and bulk data moves, because a repeat run over an unchanged tree costs almost nothing.

#platform/multiple #target/Linux #cat/FileTransfer

% rsync, file transfer, synchronisation, backup, sync, mirror, delta, incremental, ssh, snapshot, exclude, delete, bandwidth

## rsync - Check the Version and Capabilities

The version determines which options exist and which checksum and compression algorithms are available. The protocol number matters when the two ends run different releases, because the older side dictates the feature set.

```
rsync --version
```

Both ends must have rsync installed when the transfer is remote. Check the far side before debugging anything else:

```
ssh ops@server1.example.com 'rsync --version | head -1'
```

## rsync - Understand the Trailing Slash

This is the single most important rsync rule and the cause of most accidental nesting. A trailing slash on the **source** means "the contents of this directory"; no trailing slash means "this directory itself". The destination's trailing slash is irrelevant.

Copy the contents of `src` into `dest`, so `dest/a.txt` appears:

```
rsync -a src/ dest/
```

Copy the directory `src` into `dest`, so `dest/src/a.txt` appears:

```
rsync -a src dest/
```

Proven locally with a source tree holding `a.txt` and `sub/b.txt`. With the slash the destination is flat; without it an extra level is created:

```
rsync -a src/ d1/ && find d1
rsync -a src  d2/ && find d2
```

The two runs produce `d1/a.txt`, `d1/sub/b.txt` and `d2/src/a.txt`, `d2/src/sub/b.txt`. If a job silently starts producing a doubled path such as `/srv/data/data/`, a missing trailing slash is the reason. Shell tab completion appends the slash for you, which is why interactive runs and scripted runs so often disagree.

## rsync - Use Archive Mode

`-a` is the normal starting point for server-to-server copies. It is exactly equivalent to `-rlptgoD`: recurse, copy symlinks as symlinks, preserve permissions, modification times, group, owner, and device/special files.

```
rsync -a /srv/data/ /mnt/backup/data/
```

What `-a` does **not** include is worth memorising, because each is a separate flag: ACLs (`-A`), extended attributes (`-X`), access times (`-U`), creation times (`-N`), and hardlink detection (`-H`).

```
rsync -aHAX /srv/data/ /mnt/backup/data/
```

Preserving owner and group requires root on the receiving side. As an unprivileged user those parts of `-a` fail silently, so turn the sub-option off explicitly rather than wondering why ownership is wrong:

```
rsync -a --no-o --no-g /srv/data/ ~/backup/data/
```

`-r` alone recurses but preserves nothing, which is almost never what you want for a server copy:

```
rsync -r /srv/data/ /mnt/backup/data/
```

## rsync - Dry Run Before Every Real Transfer

`-n` (`--dry-run`) performs the entire file-list comparison and prints what would happen, but writes nothing. Do this before every unfamiliar rsync command — it is the only cheap way to catch a wrong trailing slash or an over-broad `--delete` before it destroys data.

```
rsync -avn --delete /srv/data/ /mnt/backup/data/
```

Combine it with `-i` so the output is the exact itemised change list the real run will produce:

```
rsync -ain --delete /srv/data/ /mnt/backup/data/
```

Note that a dry run cannot predict everything: files created by earlier steps of the same run are not visible to it, so nested transfers can differ slightly from the preview.

## rsync - Show What Is Happening

`-v` lists transferred file names. A second `-v` adds skipped files, which is how you find out *why* something was not copied.

```
rsync -av /srv/data/ /mnt/backup/data/
```

`--progress` prints a per-file percentage, rate and ETA. It is useful for a handful of large files and useless for a million small ones, since the output itself becomes the bottleneck.

```
rsync -av --progress /srv/data/ /mnt/backup/data/
```

`--info=progress2` reports a single running total for the whole transfer instead of per-file lines. Use it without `-v` so the screen is not flooded with names — this is the right choice for a large tree.

```
rsync -a --info=progress2 /srv/data/ /mnt/backup/data/
```

`-h` makes sizes human-readable; repeat it for powers of 1024 instead of 1000:

```
rsync -ah --info=progress2 /srv/data/ /mnt/backup/data/
```

## rsync - Compress in Transit

`-z` compresses the file data on the wire. It helps on a slow or metered WAN link, where the CPU has spare capacity relative to the network.

```
rsync -az /srv/data/ ops@server1.example.com:/srv/data/
```

On a fast LAN, `-z` usually makes transfers slower, not faster: a 1 Gbit/s or 10 Gbit/s link outruns single-threaded compression, so the CPU becomes the limit. It is also wasted on data that is already compressed, such as `.gz`, `.jpg`, `.mp4` or container images. Leave it off by default on-premise and measure before adding it.

Pick the algorithm explicitly when both ends are recent; `zstd` gives a much better speed/ratio trade-off than the default `zlib`:

```
rsync -az --compress-choice=zstd /srv/data/ ops@server1.example.com:/srv/data/
```

Set the compression level, and skip file types that will not compress:

```
rsync -az --compress-level=1 --skip-compress=gz/zst/jpg/mp4/iso /srv/data/ ops@server1.example.com:/srv/data/
```

## rsync - Delete Extraneous Files at the Destination

Without `--delete`, rsync only ever adds and updates; files removed from the source stay at the destination forever. `--delete` makes the destination a true mirror.

```
rsync -a --delete /srv/data/ /mnt/backup/data/
```

The danger is entirely about the trailing slash. `rsync -a --delete /srv/data /mnt/backup/` puts the tree at `/mnt/backup/data/` and deletes **everything else** under `/mnt/backup/`. Get the slash wrong on a destination that holds other data and `--delete` will remove it. Always dry-run first, and never point `--delete` at a directory that contains anything other than the mirror.

By default deletions happen as the transfer walks the tree. `--delete-after` defers them until the transfer completes, so a run that fails part-way leaves the old files intact:

```
rsync -a --delete-after /srv/data/ /mnt/backup/data/
```

Excluded files are protected from deletion by default. `--delete-excluded` removes them too, which is how you clean up a destination after tightening the exclude list:

```
rsync -a --delete --delete-excluded --exclude='*.tmp' /srv/data/ /mnt/backup/data/
```

Cap the damage a bad run can do. `--max-delete` aborts with exit code 25 once the limit is hit, leaving the remaining files alone:

```
rsync -a --delete --max-delete=100 /srv/data/ /mnt/backup/data/
```

## rsync - Exclude and Include Patterns

`--exclude` skips matching paths. A pattern with no slash matches at any depth; a leading slash anchors it to the transfer root, not the filesystem root.

```
rsync -a --exclude='*.log' --exclude='/cache/' /srv/app/ /mnt/backup/app/
```

Rules are evaluated **in the order given, first match wins**. An `--include` must therefore come before the `--exclude` it is carving an exception out of. This works:

```
rsync -a --include='app.log' --exclude='*.log' /srv/app/ /mnt/backup/app/
```

Reversing the two silently transfers nothing extra, because `--exclude='*.log'` matches first and the include is never reached:

```
rsync -a --exclude='*.log' --include='app.log' /srv/app/ /mnt/backup/app/
```

The classic trap is a whitelist. `--include='*.txt' --exclude='*'` finds only the top-level `.txt` files, because `*` excludes the subdirectories too and rsync never descends into them. Add `--include='*/'` so directories stay traversable:

```
rsync -a --include='*/' --include='*.txt' --exclude='*' /srv/app/ /mnt/backup/app/
```

Exclude a directory's contents but keep the directory itself:

```
rsync -a --exclude='/var/cache/**' /srv/app/ /mnt/backup/app/
```

## rsync - Read Rules and File Lists from a File

`--exclude-from` keeps a long rule set in version control instead of on the command line. One pattern per line; `#` starts a comment.

```
rsync -a --exclude-from=./backup-excludes.txt /srv/app/ /mnt/backup/app/
```

`--filter` is the general form, where each rule carries its own sign: `-` excludes, `+` includes. It expresses the same list in a single argument.

```
rsync -a --filter='+ *.conf' --filter='- *' /etc/app/ /mnt/backup/app-conf/
```

`--filter='dir-merge /.rsync-filter'`, abbreviated `-F`, reads per-directory rule files as it walks the tree, letting a subdirectory declare its own exclusions:

```
rsync -aF /srv/app/ /mnt/backup/app/
```

`--files-from` inverts the model: instead of transferring a tree minus exclusions, it transfers exactly the listed paths, relative to the source root. It implies `--relative`, so the directory structure is recreated, and it disables the `-r` implied by `-a`.

```
rsync -a --files-from=./manifest.txt /srv/app/ ops@server1.example.com:/srv/app/
```

Feed the list from a pipeline by reading standard input, which pairs well with `find`:

```
find /srv/app -name '*.conf' -printf '%P\n' | rsync -a --files-from=- /srv/app/ /mnt/backup/app/
```

## rsync - Preserve Hardlinks, ACLs and Extended Attributes

`-H` makes rsync detect files that share an inode at the source and recreate that sharing at the destination. It costs memory proportional to the file count, which is why `-a` leaves it out — but without it, a hardlink farm expands into full copies.

```
rsync -aH /srv/data/ /mnt/backup/data/
```

`-A` carries POSIX ACLs and `-X` carries extended attributes, including SELinux labels stored in `security.selinux`. Restoring a system tree without them produces a filesystem that looks right and fails at runtime.

```
rsync -aAX /srv/data/ /mnt/backup/data/
```

The full "copy everything faithfully" form for a server migration, with `-S` for sparse files:

```
rsync -aHAXS --numeric-ids /srv/ /mnt/newroot/
```

## rsync - Map Users and Groups Across Hosts

By default rsync translates ownership by **name**: it sends the user and group names, and the receiver looks them up in its own passwd/group databases. That silently changes numeric ownership when the two hosts have different UIDs for the same account.

`--numeric-ids` disables the translation and copies raw UID/GID values. Use it for any backup or restore, and for migrations between machines whose account databases are not identical.

```
rsync -aH --numeric-ids /srv/data/ /mnt/backup/data/
```

Force a single owner and group regardless of the source, which is the usual need when deploying application files:

```
rsync -a --chown=appuser:appgroup ./release/ /opt/app/
```

Map specific accounts rather than all of them, for example when a service account was renumbered:

```
rsync -a --usermap=1001:2001 --groupmap=www-data:nginx /srv/app/ /mnt/backup/app/
```

## rsync - Transfer over SSH

A colon in the path makes it remote, and rsync shells out to ssh by default. Both hosts need rsync installed; only the client needs the options.

```
rsync -a /srv/data/ ops@server1.example.com:/srv/data/
```

`-e` overrides the remote shell command. This is how you reach a non-standard port — note the port belongs to ssh, not to rsync, so there is no `-p` flag on rsync itself:

```
rsync -a -e "ssh -p 2222" /srv/data/ ops@server1.example.com:/srv/data/
```

Select a specific key, which is what unattended backup jobs need:

```
rsync -a -e "ssh -i /root/.ssh/id_ed25519_backup -o IdentitiesOnly=yes" /srv/data/ backup@server1.example.com:/srv/data/
```

Make a scripted transfer fail instead of hanging on a prompt, and cap the connection attempt:

```
rsync -a -e "ssh -o BatchMode=yes -o ConnectTimeout=10" /srv/data/ ops@server1.example.com:/srv/data/
```

Route through a bastion using ssh's own jump syntax:

```
rsync -a -e "ssh -J ops@bastion.example.com" /srv/data/ deploy@10.20.0.11:/srv/data/
```

Anything defined in `~/.ssh/config` — user, port, key, `ProxyJump`, `ControlMaster` — applies automatically, so a host alias collapses the whole command:

```
rsync -a /srv/data/ web1:/srv/data/
```

Run the remote side through sudo when the destination needs root but the login account is unprivileged. This requires a passwordless sudo rule for rsync on the target:

```
rsync -a --rsync-path="sudo rsync" /srv/data/ ops@server1.example.com:/srv/data/
```

## rsync - Push and Pull

Push sends local data to the remote host. The remote account needs write access to the destination, which means it also has the power to delete there.

```
rsync -a --delete /srv/data/ ops@server1.example.com:/srv/data/
```

Pull fetches remote data to the local host. Swap the arguments; the trailing-slash rule is unchanged.

```
rsync -a --delete ops@server1.example.com:/srv/data/ /mnt/backup/server1/
```

Pull is the safer direction for backups: the backup server holds the key and initiates the connection, so a compromised production host cannot reach in and wipe the archive. The reverse — production pushing to the backup server — hands every production box write access to the backups.

```
rsync -a --delete -e "ssh -i /root/.ssh/id_ed25519_backup" backup@web1:/srv/data/ /mnt/backup/web1/
```

Only one side may be remote. Copying between two remote hosts in a single command is not supported, so run it from one of them, or stage through the local machine.

```
ssh web1 'rsync -a /srv/data/ web2:/srv/data/'
```

## rsync - Limit Bandwidth

`--bwlimit` caps the transfer rate so a bulk copy does not starve production traffic on a shared uplink. The value is KiB/s by default; a suffix sets other units.

```
rsync -a --bwlimit=5000 /srv/data/ ops@server1.example.com:/srv/data/
```

Use a suffix for readability — `5m` is 5 MiB per second, roughly 40 Mbit/s:

```
rsync -a --bwlimit=5m /srv/data/ ops@server1.example.com:/srv/data/
```

The limit applies to socket I/O on the side where it is specified, and it is an average rather than a hard ceiling: rsync writes in bursts and sleeps between them. For strict shaping, use `tc` on the interface instead.

## rsync - Resume Interrupted Transfers

By default rsync writes to a temporary file and deletes it if the transfer is interrupted, so a failed run over a large file starts again from zero. `--partial` keeps the incomplete file so the next run resumes from it.

```
rsync -a --partial /srv/backups/db.dump ops@server1.example.com:/srv/backups/
```

`-P` is the shorthand for `--partial --progress`, which is what most people actually type for a long interactive transfer:

```
rsync -aP /srv/backups/db.dump ops@server1.example.com:/srv/backups/
```

`--partial-dir` puts the fragment in a side directory instead of leaving a truncated file at the real destination path. Do this for anything another process might pick up — a half-written file at the final name is worse than no file.

```
rsync -a --partial-dir=.rsync-partial /srv/backups/ ops@server1.example.com:/srv/backups/
```

`--append-verify` assumes the destination file is a prefix of the source, appends only the missing tail, then checksums the whole result to confirm. It is right for append-only data such as log archives, and wrong for anything whose earlier bytes may have changed — for those, the ordinary delta transfer is both safe and cheap.

```
rsync -a --append-verify /var/log/archive/ ops@server1.example.com:/var/log/archive/
```

`--timeout` aborts a stalled transfer rather than letting a cron job hang until the next one starts:

```
rsync -a --timeout=300 --partial /srv/data/ ops@server1.example.com:/srv/data/
```

## rsync - Control How Files Are Compared

rsync's default quick check skips a file when its size **and** modification time both match. This is fast because it needs no reads, and it is right almost always.

```
rsync -a /srv/data/ /mnt/backup/data/
```

`-c` reads and checksums both copies instead. Use it when mtimes are untrustworthy — after a restore, a `touch`-happy build, or a filesystem that lost timestamps. It is far slower because every byte on both sides is read.

```
rsync -ac /srv/data/ /mnt/backup/data/
```

Proven locally: a destination file with correct content but a mangled timestamp is re-transferred by the default check (itemised `>f..t......`) and only has its timestamp corrected under `-c` (`.f..t......`), with no data on the wire.

```
rsync -ain -c /srv/data/ /mnt/backup/data/
```

`--size-only` ignores timestamps entirely and compares size alone. It suits mirrors of content that is never edited in place, and it will happily miss a same-size change:

```
rsync -a --size-only /srv/data/ /mnt/backup/data/
```

`--ignore-times` goes the other way and disables the quick check completely, transferring every file regardless. It still uses the delta algorithm, so unchanged blocks are not resent, but it reads everything:

```
rsync -a --ignore-times /srv/data/ /mnt/backup/data/
```

Pick a faster checksum algorithm when `-c` is unavoidable; `xxh128` is dramatically faster than MD5 on large trees:

```
rsync -ac --checksum-choice=xxh128 /srv/data/ /mnt/backup/data/
```

## rsync - Skip Files That Are Newer at the Destination

`-u` (`--update`) refuses to overwrite a destination file whose modification time is newer than the source's. It protects changes made directly on the target from being clobbered by a stale source.

```
rsync -au /srv/data/ /mnt/backup/data/
```

Verified locally: after editing a file at the destination, `rsync -au` leaves it alone while a plain `rsync -a` overwrites it. Note this is a timestamp comparison, not a merge — it is a safety net for one-directional syncs, not two-way replication. rsync cannot do two-way sync at all; reach for `unison` or a filesystem-level tool for that.

```
rsync -aun /srv/data/ /mnt/backup/data/
```

## rsync - Keep Backups of Overwritten Files

`-b` renames each file that is about to be overwritten or deleted instead of discarding it. The default suffix is `~`, and the backup lands beside the original.

```
rsync -ab /srv/app/ /mnt/backup/app/
```

`--backup-dir` moves the old versions into a separate tree, mirroring the original directory structure. This keeps the live destination clean, which matters when it is served by a web server or scanned by an application.

```
rsync -ab --backup-dir=/mnt/backup/previous /srv/app/ /mnt/backup/app/
```

Confirmed locally: with `--backup-dir=/path/prev`, overwriting `a.txt` and `sub/b.txt` produces `prev/a.txt` and `prev/sub/b.txt`. Note that `--backup-dir` also changes the default suffix to empty, so set `--suffix` explicitly if you still want one.

```
rsync -ab --backup-dir=/mnt/backup/previous --suffix=.bak /srv/app/ /mnt/backup/app/
```

Date the backup directory to get a crude version history from a nightly job:

```
rsync -ab --backup-dir="/mnt/backup/previous/$(date +%F)" --delete /srv/app/ /mnt/backup/app/
```

## rsync - Build Incremental Snapshots with Hardlinks

`--link-dest` compares against a reference directory and, for every file that is unchanged, creates a hardlink to the reference copy instead of transferring or duplicating data. Each snapshot is a complete browsable tree, but only changed files consume disk.

```
rsync -a --delete --link-dest=/mnt/backup/daily.1 /srv/data/ /mnt/backup/daily.0/
```

Proven locally with `ls -li`: an unchanged file has the **same inode number** in both snapshots with a link count of 2, while a new file has its own inode and a link count of 1. `du` on the second snapshot reports only the new data.

```
stat -c '%i %h %n' /mnt/backup/daily.1/a.txt /mnt/backup/daily.0/a.txt
```

A rotating nightly job. `--delete` is essential: without it, files removed from the source persist in every future snapshot.

```
rm -rf /mnt/backup/daily.7
for i in 6 5 4 3 2 1 0; do [ -d "/mnt/backup/daily.$i" ] && mv "/mnt/backup/daily.$i" "/mnt/backup/daily.$((i+1))"; done
rsync -a --delete --link-dest=/mnt/backup/daily.1 /srv/data/ /mnt/backup/daily.0/
```

Two caveats. A relative `--link-dest` path is resolved against the **destination** directory, not the current one, so use absolute paths in scripts. And because the snapshots share inodes, editing a file in one snapshot in place edits it in all of them — treat the whole archive as read-only, and delete a snapshot only with `rm -rf` on the whole directory.

```
rsync -a --delete --link-dest=/mnt/backup/daily.1 --exclude='/tmp/' /srv/data/ /mnt/backup/daily.0/
```

## rsync - Read the Itemised Change Output

`-i` prints an eleven-character code per file, in the form `YXcstpoguax`. The first character is the update type, the second the file type, and the rest name the attributes being changed. It is the most precise way to see what a run did, and it composes with `-n`.

```
rsync -ain /srv/data/ /mnt/backup/data/
```

Position 1 is `<` for sent to a remote host, `>` for received locally, `c` for a local creation such as a directory, `h` for a hardlink, `.` for no update, and `*` for a message like `deleting`. Position 2 is `f` file, `d` directory, `L` symlink, `D` device, `S` special. The remaining columns are `c` checksum, `s` size, `t` time, `p` perms, `o` owner, `g` group, `u` atime, `a` ACL, `x` xattr — a dot means unchanged, a `+` means the item is newly created.

Codes observed locally, each one reproduced against a real tree:

```
>f+++++++++ a.txt        new file, everything is new
cd+++++++++ sub/         directory created at the destination
>f.st...... a.txt        content changed: size and time being updated
.f...p..... sub/b.txt    permissions only, no data transferred
.d..t...... ./           directory timestamp only
*deleting   stale.txt    removed by --delete
```

Repeat the flag as `-ii` to list unchanged files as well, which turns the output into a full inventory:

```
rsync -aiin /srv/data/ /mnt/backup/data/
```

`--out-format` produces the same information in a shape a log parser can consume:

```
rsync -a --out-format='%i %n %l' /srv/data/ /mnt/backup/data/ >> /var/log/sync.log
```

## rsync - Print Transfer Statistics

`--stats` appends a summary: file counts, how many were created and deleted, total size, and the split between literal data actually sent and matched data reconstructed from the destination copy.

```
rsync -a --stats /srv/data/ /mnt/backup/data/
```

The `speedup` figure at the end is total size divided by bytes sent. A high number means the delta algorithm is working; a speedup near 1 on a repeat run means files are being re-transferred, which usually points at a timestamp or ownership problem rather than real changes.

```
rsync -ah --stats /srv/data/ ops@server1.example.com:/srv/data/ | tail -20
```

Cut the noise in a cron job to just the summary line:

```
rsync -a --stats /srv/data/ /mnt/backup/data/ | grep -E 'Total (transferred )?file size|speedup'
```

## rsync - Handle Sparse Files

`-S` detects runs of nulls and writes them as holes rather than real blocks. Without it, a sparse VM disk image or database file expands to its full apparent size at the destination.

```
rsync -aS /var/lib/libvirt/images/ /mnt/backup/images/
```

Measured locally on a 64 MiB file containing only holes: `rsync -a` produced a 64 MiB destination file, `rsync -aS` produced one occupying zero blocks. `du` shows the difference that `ls -l` hides.

```
du -h /mnt/backup/images/disk.qcow2
```

`-S` and `--inplace` were mutually exclusive in older releases; since 3.1.3 they can be combined, which is what you want for repeatedly syncing a large image without doubling the space during the copy:

```
rsync -aS --inplace /var/lib/libvirt/images/disk.qcow2 /mnt/backup/images/
```

## rsync - Set Permissions on the Destination

`--chmod` applies mode changes as files are written, without touching the source. `D` prefixes a rule for directories and `F` for files, so directories can stay traversable while files do not become executable.

```
rsync -a --chmod=D755,F644 ./release/ /opt/app/
```

Verified locally: `--chmod=D755,F640` produced `drwxr-xr-x` directories and `-rw-r-----` files at the destination regardless of the source modes.

```
rsync -a --chmod=D755,F640 ./release/ /opt/app/
```

Symbolic rules work too, which is the readable way to strip group and other write access:

```
rsync -a --chmod=go-w ./release/ /opt/app/
```

`--perms` is implied by `-a`; turn it off with `--no-p` when the destination filesystem manages its own permissions, for example an SMB or FAT mount:

```
rsync -rlt --no-p --no-g --no-o /srv/data/ /mnt/share/data/
```

## rsync - Create Missing Destination Directories

rsync creates the final directory but not missing parents, so a destination path several levels deep fails. `--mkpath`, added in 3.2.3, creates the whole path.

```
rsync -a --mkpath ./release/ /opt/app/releases/2026-08-02/
```

Verified locally: `rsync -a --mkpath src/a.txt mk/deep/path/` created `mk/deep/path` and placed the file inside it.

```
rsync -a --mkpath /srv/data/ ops@server1.example.com:/srv/archive/2026/08/
```

`-R` (`--relative`) is the other way to build structure: it recreates the source path as given, which is useful for gathering scattered files into one archive tree.

```
rsync -aR /srv/app/./config/nginx.conf /mnt/backup/
```

## rsync - Connect to an rsync Daemon

A double colon, or an `rsync://` URL, talks to an rsync daemon instead of tunnelling over ssh. There is no shell and no per-user account: the daemon exposes named **modules**, each mapped to a directory in `/etc/rsyncd.conf`.

```
rsync rsync://mirror.example.com/
```

List the contents of one module:

```
rsync mirror.example.com::debian/
```

Pull from a module. The path after the module name is relative to the module's root:

```
rsync -a rsync://mirror.example.com/debian/dists/ /srv/mirror/dists/
```

Authenticate against a daemon that requires it, reading the password from a file so it never appears in the process list. The file must be mode 600 or rsync refuses it.

```
rsync -a --password-file=/etc/rsync-backup.pass backup@server1.example.com::data/ /mnt/backup/data/
```

Daemon traffic is unencrypted, so on any untrusted network run the daemon protocol inside an ssh tunnel rather than exposing port 873:

```
rsync -a -e "ssh -p 2222" --rsync-path="rsync --config=/etc/rsyncd.conf" ops@server1.example.com:/srv/data/ /mnt/backup/data/
```

## rsync - Check Exit Codes in Scripts

rsync's exit status is specific enough to distinguish "nothing to do" from "the link died". A cron wrapper that only checks for non-zero will page you for harmless conditions.

```
rsync -a --delete /srv/data/ /mnt/backup/data/; echo "rc=$?"
```

The values that matter on-premise, all documented in the 3.2.7 man page and the first three confirmed locally: `0` success, `1` syntax or usage error, `2` protocol incompatibility, `3` errors selecting input files or directories, `5` error starting the client-server protocol, `10`/`11` socket or file I/O error, `12` protocol data stream error, `20` interrupted by SIGINT or SIGUSR1, `23` partial transfer due to error, `24` partial transfer due to vanished source files, `25` stopped by `--max-delete`, `30`/`35` timeout.

```
rsync -a ./missing-source/ /mnt/backup/data/ >/dev/null 2>&1; echo "rc=$?"
```

Code 24 is the common false alarm: it means a file disappeared between the file-list scan and the transfer, which is normal when syncing live directories such as spools or log trees. Treat it as success:

```
rsync -a /var/spool/app/ /mnt/backup/spool/; rc=$?; [ "$rc" -eq 0 ] || [ "$rc" -eq 24 ] || exit "$rc"
```

Code 23 usually means a permission error on individual files rather than a broken transfer, so log the run and inspect it rather than blindly retrying:

```
rsync -a --info=stats2 /srv/data/ /mnt/backup/data/ >> /var/log/sync.log 2>&1 || echo "rsync failed rc=$?" >&2
```
