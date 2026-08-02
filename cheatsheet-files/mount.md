# mount

mount attaches a filesystem to a directory in the running kernel's mount tree, and umount detaches it. `/etc/fstab` records the mounts that should be established at boot, so anything that must survive a reboot belongs there rather than in a shell history.

#platform/multiple #target/Linux #cat/Storage

% mount, fstab, filesystems, storage, findmnt, umount, blkid, lsblk, nfs, bind, tmpfs, loop, uuid

## mount - List Currently Mounted Filesystems

Run with no arguments to dump every mount the kernel knows about. The output is unsorted, unfiltered, and includes dozens of pseudo-filesystems, which is why it is rarely the right tool on a real server.

```
mount
```

The same information straight from the kernel, which is what `mount` actually reads:

```
cat /proc/mounts
```

## mount - Inspect Mounts With findmnt

findmnt reads the same kernel tables but renders them as a tree and accepts filters, so it is the better default for inspection. The tree shows parent/child relationships, which matters because a child mount hides the directory underneath it.

```
findmnt
```

Print a flat list instead of a tree, which is easier to grep or paste into a ticket:

```
findmnt -l
```

Show only real block-device filesystems and skip the pseudo ones:

```
findmnt --real
```

Show only the pseudo-filesystems (proc, sysfs, cgroup2, tmpfs, and friends):

```
findmnt --pseudo
```

Restrict to one or more filesystem types:

```
findmnt -t ext4,xfs,vfat
```

## mount - Search Mounts by Target or Source

Resolve a path to the filesystem that actually backs it. `-T` accepts any path, not just a mountpoint, and reports the nearest enclosing mount — the quickest way to answer "which disk is this directory on".

```
findmnt -T /var/lib/postgresql
```

Look up by source device instead:

```
findmnt -S /dev/mapper/vg0-data
```

Look up by UUID or label without needing the device node:

```
findmnt -S UUID=8747f0ed-c7df-4764-b524-4cc86d1ab4ea
```

Show a mountpoint together with everything mounted beneath it:

```
findmnt -R /boot
```

## mount - Choose the Output Columns

Pick the exact fields to print. `findmnt --help` lists every available column.

```
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS,SIZE,USED
```

Drop the header and print a single value, which is the form to use in scripts:

```
findmnt -n -o SOURCE --target /
```

Show only the filesystem-specific options, separated from the generic VFS ones:

```
findmnt -o TARGET,VFS-OPTIONS,FS-OPTIONS
```

## mount - Output Mounts as JSON

Emit structured output for a config-management check or a monitoring script, instead of parsing columns with awk.

```
findmnt -J
```

Combine with a filter and pipe into jq:

```
findmnt -J -t ext4 | jq -r '.filesystems[].target'
```

## mount - Show Space Usage per Mount

Print a df-style view built from the mount table, so the mountpoint and its usage line up without cross-referencing two commands.

```
findmnt --df
```

## mount - Find a Filesystem UUID or Label

Every filesystem carries a UUID generated at mkfs time. Print the identifiers for all block devices.

```
lsblk -f
```

The same, from the blkid cache. Without root this may return nothing or a stale subset, so re-run it with sudo when a freshly created filesystem is missing.

```
blkid
```

Extract just the UUID of one device, for pasting into fstab:

```
blkid -s UUID -o value /dev/nvme0n1p2
```

Show partition-level identifiers as well, which are what `PARTUUID=` in fstab refers to:

```
lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,PARTUUID,MOUNTPOINTS
```

## mount - Mount a Filesystem by Device

The classic form: source device, then target directory. The mountpoint must already exist and should be empty, because anything already in it becomes inaccessible while the mount is active.

```
mount /dev/sdb1 /mnt/data
```

State the filesystem type explicitly rather than letting libblkid guess:

```
mount -t xfs /dev/sdb1 /mnt/data
```

Create the mountpoint directory in the same call if it does not exist:

```
mount --mkdir /dev/sdb1 /mnt/data
```

## mount - Mount by UUID or Label

Kernel device names such as `/dev/sdb` are assigned in hardware-detection order and can change when a disk is added, removed, or fails to spin up. The UUID lives inside the filesystem itself and never moves, which is why it is the only safe identifier for a persistent configuration.

```
mount UUID=8747f0ed-c7df-4764-b524-4cc86d1ab4ea /mnt/data
```

Equivalent using the dedicated flag:

```
mount -U 8747f0ed-c7df-4764-b524-4cc86d1ab4ea /mnt/data
```

Mount by filesystem label, which is readable but not guaranteed unique across disks:

```
mount -L backup-vol /mnt/backup
```

```
mount LABEL=backup-vol /mnt/backup
```

## mount - Mount Read-Only

Mount without write access. Use this for forensic work, for recovering data off a suspect disk, and for any filesystem the workload only ever reads.

```
mount -o ro /dev/sdb1 /mnt/data
```

The short flag does the same thing:

```
mount -r /dev/sdb1 /mnt/data
```

## mount - Remount With Different Options

Change the flags on an already-mounted filesystem without detaching it. Flipping to read-only is the standard first move before running a filesystem check or taking a snapshot.

```
mount -o remount,ro /mnt/data
```

Flip it back to read-write:

```
mount -o remount,rw /mnt/data
```

When only the mountpoint is given, mount merges the new options with the entry from fstab. Giving both device and mountpoint replaces the option set outright:

```
mount -o remount,rw /dev/sdb1 /mnt/data
```

Re-apply the options from fstab after editing that file, without a reboot:

```
mount -o remount /mnt/data
```

## mount - Create a Bind Mount

A bind mount makes an existing directory subtree visible at a second path. Nothing is copied and no new filesystem is involved — it is another reference to the same inodes, which is how a large data directory gets exposed under a service's expected path without moving it.

```
mount --bind /srv/data /var/www/html/data
```

`--bind` attaches only the one filesystem. Use `--rbind` to carry any submounts along with it, which is what you want when the source tree has other filesystems mounted inside it:

```
mount --rbind /srv/data /var/www/html/data
```

Create a read-only bind in a single call:

```
mount -o bind,ro /srv/data /var/www/html/data
```

The classic two-step form, still needed on older util-linux, since the first bind ignores `ro`:

```
mount --bind /srv/data /var/www/html/data
mount -o remount,bind,ro /srv/data /var/www/html/data
```

Bind mounts are the mechanism behind container volume mounts: the runtime binds a host path into the container's mount namespace, so `findmnt` on the host shows the same inodes reachable from two places.

## mount - Common Filesystem-Independent Options

These options work on essentially any filesystem and are passed with `-o` or written into the fourth fstab field.

```
defaults    rw, suid, dev, exec, auto, nouser, async
ro / rw     read-only or read-write
noatime     never update inode access times; implies nodiratime
relatime    update atime only if older than mtime/ctime (kernel default)
nodev       ignore device nodes on the filesystem
nosuid      ignore setuid/setgid bits and file capabilities
noexec      refuse to execute binaries from the filesystem
noauto      skip this entry during mount -a and at boot
nofail      do not fail the boot if the device is absent
_netdev     wait for the network before attempting the mount
discard     issue TRIM to the block device as blocks are freed
```

`nodev,nosuid,noexec` together are the standard hardening set for any filesystem holding untrusted or user-writable data — `/tmp`, `/var/tmp`, `/home`, and removable media:

```
mount -o defaults,nodev,nosuid,noexec /dev/sdb1 /mnt/upload
```

`noatime` removes a metadata write on every read, which is a measurable win on busy read-heavy filesystems:

```
mount -o defaults,noatime /dev/sdb1 /srv/data
```

## mount - Mount a tmpfs

tmpfs lives in memory and page cache, so its contents vanish on reboot. Use it for scratch space, build directories, and anything holding secrets that should never touch a disk.

```
mount -t tmpfs -o size=2G tmpfs /mnt/scratch
```

Size accepts a percentage of physical RAM, and the permissions can be pinned at mount time:

```
mount -t tmpfs -o size=10%,mode=1777,nodev,nosuid,noexec tmpfs /mnt/scratch
```

The fstab equivalent:

```
tmpfs  /mnt/scratch  tmpfs  defaults,size=2G,mode=1777,nodev,nosuid,noexec  0  0
```

## mount - Mount an ISO or Image File Over Loop

A regular file containing a filesystem is mounted through a loop device. mount allocates one automatically when the filesystem type is recognisable, and frees it again on umount.

```
mount -o loop,ro /srv/iso/ubuntu.iso /mnt/iso
```

Be explicit about the type for an ISO 9660 image:

```
mount -t iso9660 -o loop,ro /srv/iso/ubuntu.iso /mnt/iso
```

Mount a partition inside a whole-disk image by skipping to its byte offset:

```
mount -o loop,offset=1048576 /srv/images/disk.img /mnt/img
```

List the loop devices currently in use, and release one by hand if a mount was torn down uncleanly:

```
losetup -a
losetup -d /dev/loop3
```

## mount - Mount an NFS Export

NFS sources are written `<host>:<export>`. The mount goes through the `/sbin/mount.nfs` helper, so `nfs-common` (or the distribution equivalent) has to be installed.

```
mount -t nfs 10.0.0.10:/exports/data /mnt/data
```

Pin the protocol version rather than negotiating it, so a server upgrade cannot silently change behaviour:

```
mount -t nfs -o vers=4.2 10.0.0.10:/exports/data /mnt/data
```

In fstab, a network filesystem must carry `_netdev` so the mount is deferred until networking is up; without it the boot attempts the mount too early and fails. `nofail` keeps a dead NFS server from blocking the boot entirely:

```
10.0.0.10:/exports/data  /mnt/data  nfs  defaults,_netdev,nofail,soft,timeo=60  0  0
```

`hard` (the default) makes I/O retry indefinitely when the server disappears, which hangs processes but never loses writes; `soft` returns errors instead. Prefer `hard` for anything holding real data.

## mount - Understand the /etc/fstab Fields

Each non-comment line has six whitespace-separated fields. Getting the last two wrong is a common cause of surprising boot behaviour.

```
# <device>        <mountpoint>  <fstype>  <options>              <dump> <pass>
UUID=8747f0ed-...  /srv/data     ext4      defaults,noatime,nofail  0      2
```

```
1 device      block device, UUID=, LABEL=, PARTUUID=, host:/export for NFS
2 mountpoint  target directory; "none" for swap and bind sources
3 fstype      ext4, xfs, vfat, tmpfs, nfs, swap, auto, ...
4 options     comma-separated mount options; use "defaults" as the base
5 dump        dump(8) backup flag; effectively always 0 on modern systems
6 pass        fsck order at boot: 0 = never check, 1 = root only, 2 = everything else
```

Read the parsed fstab back rather than eyeballing the file, which catches a mistyped field immediately:

```
findmnt -s
```

Compare the fstab entry against what is actually mounted:

```
findmnt -s -o TARGET,SOURCE,FSTYPE,OPTIONS,FREQ,PASSNO
```

## mount - Keep a Server Bootable With nofail

Without `nofail`, systemd treats a failed mount as a fatal dependency of `local-fs.target`. If the device is missing at boot — a pulled disk, a renamed device node, an unreachable SAN LUN — the boot stops in the emergency shell and the machine needs console access to recover. On a remote or headless server that is an outage.

```
UUID=8747f0ed-c7df-4764-b524-4cc86d1ab4ea  /srv/data  ext4  defaults,nofail  0  2
```

Add a bounded timeout so systemd gives up instead of waiting out its default, and keep `_netdev` on anything that needs the network:

```
10.0.0.10:/exports/data  /mnt/data  nfs  defaults,_netdev,nofail,x-systemd.mount-timeout=30  0  0
```

Use `noauto` for a device that should exist in fstab as a named recipe but never be mounted automatically:

```
/dev/sdc1  /mnt/archive  ext4  defaults,noauto  0  0
```

## mount - Verify fstab Before Rebooting

`findmnt --verify` parses `/etc/fstab` and checks every entry — that the source resolves, the mountpoint exists, the filesystem type is plausible — without mounting anything. mount(8) explicitly names this as the recommended way to check fstab. Run it after every edit; a reboot is the only other way to find out, and by then it is too late.

```
findmnt --verify
```

Add `--verbose` to see each entry as it is checked, including the ones that pass:

```
findmnt --verify --verbose
```

Warnings about "cannot detect on-disk filesystem type (Permission denied)" simply mean the check ran unprivileged; re-run with sudo for a complete result.

Mounting everything in fstab that is not already mounted and not marked `noauto`:

```
mount -a
```

`mount -a` is a poor validation tool: it stops at the first failure, it can leave the system half-mounted, and it happily succeeds on entries that would still break the boot. Use `findmnt --verify` to check, and `mount -a` only to apply.

## mount - Reload systemd After Editing fstab

On a systemd host, `/etc/fstab` is not consulted at mount time by the service manager. `systemd-fstab-generator` converts each entry into a `.mount` unit when the manager's configuration is loaded, so an edited fstab is invisible to systemd until the units are regenerated. Skipping this step produces the classic failure where `mount -a` works fine by hand but the mount never comes back after a reboot, or where `systemctl stop` on a stale unit unmounts something you just added.

```
systemctl daemon-reload
```

Then bring up the new entries through systemd rather than through mount directly:

```
systemctl restart local-fs.target
```

Inspect the generated unit for one mountpoint. Unit names are the escaped path, so `/srv/data` becomes `srv-data.mount`:

```
systemctl status srv-data.mount
systemctl cat srv-data.mount
```

## mount - Unmount a Filesystem

Detach a filesystem by mountpoint. Using the mountpoint rather than the device is unambiguous when the same device is mounted more than once.

```
umount /mnt/data
```

Unmount a mountpoint and everything nested beneath it, deepest first:

```
umount -R /mnt/data
```

Detach the mount from the tree immediately and clean up references when the last user goes away. This is the tool for an NFS share whose server is gone — but the filesystem is not actually released yet, so re-mounting the same source before it settles can corrupt it:

```
umount -l /mnt/data
```

Force an unmount, intended for an unreachable NFS server. It does not guarantee umount will not hang, and it does not help with a busy local filesystem:

```
umount -f /mnt/nfs
```

## mount - Find What Is Holding a Mount Busy

`target is busy` means a process has a file open, a working directory, or a memory mapping inside the mount. Identify it rather than reaching for `-l` or `-f`, because killing the holder is almost always the correct fix.

```
lsof +D /mnt/data
```

fuser is faster on a large tree, since it queries the mount rather than walking it:

```
fuser -vm /mnt/data
```

Kill everything holding the mount, after reviewing the list above:

```
fuser -km /mnt/data
```

Check whether a nested mount is what is holding the parent, which `lsof` will not reveal:

```
findmnt -R /mnt/data
```

## mount - Control Mount Propagation

Every mount carries a propagation flag deciding whether mounts created under it are visible in other mount namespaces. This is what makes a container runtime's bind mounts appear or not appear on the host, and it is the reason a mount inside a namespace can be invisible outside it.

```
findmnt -o TARGET,PROPAGATION
```

Make a subtree private, so mounts created under it do not propagate outward:

```
mount --make-private /mnt/data
```

Apply the change recursively to every mount beneath the point:

```
mount --make-rprivate /mnt/data
```

Make a subtree shared, which container runtimes require when they need host-created mounts to appear inside a running container:

```
mount --make-rshared /
```

The kernel does not allow changing multiple propagation flags in one syscall, so these are separate calls and cannot be combined with other mount options.

## mount - Check Whether a Path Is a Mountpoint

Test a path and print the answer. This distinguishes a real mount from an ordinary directory that merely looks like one, which matters when a filesystem silently failed to mount and a service started writing into the empty mountpoint on the root disk instead.

```
mountpoint /mnt/data
```

Exit-status-only form for scripts: 0 if it is a mountpoint, 32 if it is not.

```
mountpoint -q /mnt/data
```

Guard a backup or write job so it cannot run against the wrong filesystem:

```
mountpoint -q /mnt/backup || { echo "backup volume not mounted" >&2; exit 1; }
```

Print the major:minor device number of the filesystem mounted there:

```
mountpoint -d /mnt/data
```
