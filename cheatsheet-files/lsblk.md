# lsblk

lsblk lists the block devices the kernel knows about, reading sysfs and the udev database rather than probing the disks. It shows disks, partitions, LUKS containers, LVM volumes and loop devices as a dependency tree, which makes it the first command to run when working out how storage is stacked on a server.

#platform/multiple #target/Linux #cat/Storage

% lsblk, block devices, disks, storage, partitions, lvm, filesystems, util-linux, udev, sysfs

## lsblk - Show the Default Device Tree

Print every block device except RAM disks, as a tree of parents and children.

```
lsblk
```

The columns are NAME, MAJ:MIN (the kernel major:minor device number), RM (removable), SIZE, RO (read-only), TYPE and MOUNTPOINTS. Indentation is the dependency relationship, so a partition sits under its disk and an LVM logical volume sits under whatever holds it. A typical encrypted server stack reads disk -> part -> crypt -> lvm:

```
NAME                        MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
nvme0n1                     259:0    0 953.9G  0 disk
├─nvme0n1p1                 259:1    0     1G  0 part  /boot/efi
├─nvme0n1p2                 259:2    0     2G  0 part  /boot
└─nvme0n1p3                 259:3    0 950.8G  0 part
  └─dm_crypt-0              252:0    0 950.8G  0 crypt
    └─ubuntu--vg-ubuntu--lv 252:1    0 950.8G  0 lvm   /
```

The default column set is explicitly documented as subject to change between releases, so never parse it in a script — always pass `--output`.

## lsblk - Show Filesystem Information

Replace the default columns with filesystem type, version, label, UUID and usage. This is the fastest way to see what is formatted, what is mounted and how full it is.

```
lsblk -f
```

`-f` is a shorthand for an explicit column list, so it can be reproduced or extended by hand:

```
lsblk -o NAME,FSTYPE,FSVER,LABEL,UUID,FSAVAIL,FSUSE%,MOUNTPOINTS
```

## lsblk - Select Columns

Choose exactly the columns needed. Explicit column lists are stable across util-linux versions, unlike the default output.

```
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,UUID,MODEL,SERIAL,ROTA,TYPE
```

Append to the default set instead of replacing it by prefixing the list with a plus:

```
lsblk -o +UUID
```

## lsblk - List Every Available Column

Dump all columns at once. Useful for discovering what data exists before pinning down a `-o` list, though the output is very wide and best sent through a pager.

```
lsblk -O
```

Restrict it to one device to keep it readable:

```
lsblk -O /dev/nvme0n1
```

The names and meanings of every column are printed at the end of the help text:

```
lsblk --help
```

## lsblk - Print a Flat List Instead of a Tree

Drop the tree drawing so each device is one self-contained line. Since util-linux 2.34 each device appears exactly once in list mode.

```
lsblk -l
```

Force tree output back on even when another option would disable it, optionally drawing the tree inside a column other than NAME:

```
lsblk -T=SIZE -o NAME,SIZE,TYPE
```

Use ASCII line-drawing characters when the output goes somewhere that cannot render UTF-8 box drawing:

```
lsblk -i
```

## lsblk - Suppress Headings for Scripting

Remove the header line so the first line of output is already data.

```
lsblk -n -o NAME,SIZE,TYPE
```

Combined with `-d` this gives a single clean value, for example the UUID to paste into fstab:

```
lsblk -dno UUID /dev/nvme0n1p2
```

## lsblk - Produce Machine-Readable Output

Raw mode drops the column padding and separates fields with single spaces. Unsafe characters in NAME, KNAME, LABEL, PARTLABEL and MOUNTPOINT are hex-escaped as `\x<code>`.

```
lsblk -rn -o NAME,SIZE,TYPE
```

Pairs mode emits `KEY="value"` per device, which is unambiguous even when a value is empty or contains spaces — a mount point like `/mnt/data backup` would silently shift the fields in raw or default output.

```
lsblk -P -o NAME,SIZE,FSTYPE,MOUNTPOINT
```

Because each line is valid shell assignment syntax, a pairs line can be consumed directly:

```
lsblk -P -o NAME,SIZE,TYPE | while read -r line; do eval "$line"; echo "dev=$NAME type=$TYPE size=$SIZE"; done
```

Column names containing characters that are illegal in shell variables (`MIN-IO`, `FSUSE%`) need `-y`, which rewrites them to `MIN_IO` and `FSUSE_PCT`:

```
lsblk -P -y -o NAME,FSUSE%,MIN-IO
```

`-P` and `-J` are the two formats maintained for backwards compatibility. Parse one of those; never parse the human-readable table.

## lsblk - Output JSON

Emit the device tree as JSON, with children nested under their parent. Pair it with an explicit `-o` list so the key set is fixed.

```
lsblk -J -o NAME,SIZE,FSTYPE,MOUNTPOINTS
```

Note that `MOUNTPOINTS` becomes a JSON array (a device can be mounted in several places), while `MOUNTPOINT` is a single string or null.

## lsblk - Filter JSON Output With jq

Because children are nested, a top-level `.blockdevices[]` only sees whole disks. That is exactly what you want for a hardware inventory — here rotational disks are reported as HDD and everything else as SSD, with sizes in bytes so they can be summed:

```
lsblk -J -b -o NAME,SIZE,TYPE,ROTA,MODEL | jq -r '.blockdevices[] | select(.type=="disk") | "\(.name)\t\(.size)\t\(if .rota then "HDD" else "SSD" end)\t\(.model)"'
```

To reach partitions and LVM volumes at any depth, recurse with `..` and filter on objects. This lists every partition that has no mount point, which is how to spot a disk that was added but never mounted:

```
lsblk -J -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT | jq -r '.. | objects | select(.type=="part" and .mountpoint==null) | "\(.name) \(.size) \(.fstype // "no filesystem")"'
```

The same recursion turns `-f` into a usage report across the whole stack:

```
lsblk -J -f | jq -r '.. | objects | select(."fsuse%" != null) | "\(.name) \(."fsuse%") \(.mountpoints[0])"'
```

## lsblk - Print Sizes in Bytes

Human-readable sizes are rounded and use 1024-based units abbreviated to a single letter, so `953.9G` really means GiB. Pass `-b` when the number has to be compared, summed or fed to another tool.

```
lsblk -b -o NAME,SIZE,TYPE
```

## lsblk - Include Empty and Hidden Devices

By default lsblk hides RAM disks. `-a` disables every built-in filter and shows empty devices and RAM disks as well, which is how to confirm that a device node exists at all after a hotplug.

```
lsblk -a
```

The near-inverse switch `-A` goes the other way and hides empty devices, trimming empty card readers and unpopulated slots from the listing:

```
lsblk -A
```

## lsblk - Exclude Loop Devices

Loop devices use major number 7. On any host running snaps or container images, dozens of them bury the real disks. Excluding major 7 restores a readable listing.

```
lsblk -e 7
```

Exclude several majors at once with a comma-separated list — 7 for loop and 11 for optical drives:

```
lsblk -e 7,11
```

The complement is `-I`, which shows only the given majors — 259 is blk_ext, used by NVMe namespaces, and 8 is sd*:

```
lsblk -I 259
```

Both filters apply to top-level devices only, so a device-mapper child of an included disk still appears.

## lsblk - Inspect a Single Device

Pass a device node to limit the output to that device and everything stacked on top of it.

```
lsblk /dev/nvme0n1
```

Add `-d` to suppress holders and slaves, giving one line for the device itself:

```
lsblk -d /dev/nvme0n1
```

Print full paths instead of bare names, so the output can be pasted straight into another command. Device-mapper devices render as their `/dev/mapper/` path:

```
lsblk -p -o NAME,SIZE,MOUNTPOINT
```

## lsblk - Walk the Stack in Reverse

Show what a device depends on rather than what depends on it. Given a logical volume, this answers "which physical disk is this actually on" in one command.

```
lsblk -s /dev/mapper/ubuntu--vg-ubuntu--lv
```

## lsblk - Show Topology

Print alignment and I/O sizing. `PHY-SEC` versus `LOG-SEC` exposes 512e drives — 4096-byte physical sectors presented as 512-byte logical ones — where a partition not aligned to the physical sector size causes read-modify-write on every I/O.

```
lsblk -t
```

`ALIGNMENT` is the alignment offset in bytes and must be 0; anything else means the partition table is misaligned against the hardware. `MIN-IO` and `OPT-IO` are the minimum and optimal I/O sizes, which matter when picking a RAID stripe or a database block size. `SCHED` is the active I/O scheduler and `RA` the read-ahead in 512-byte sectors.

The same fields are available individually:

```
lsblk -o NAME,ALIGNMENT,PHY-SEC,LOG-SEC,MIN-IO,OPT-IO,SCHED,RA
```

## lsblk - Show Discard and TRIM Support

Print the discard capabilities of each device. A `DISC-MAX` of 0B means the device or the layer above it does not support TRIM/UNMAP, so `fstrim` will do nothing there.

```
lsblk -D
```

This is the quick way to confirm that discard passes through a stack: on a LUKS or LVM device the columns read 0B unless the mapping was created with discards enabled.

## lsblk - Show Transport and SCSI Information

Print the transport type to tell local NVMe apart from SATA, USB, iSCSI or Fibre Channel attachments.

```
lsblk -d -o NAME,TRAN,TYPE,SIZE,MODEL
```

List only SCSI devices with their Host:Channel:Target:Lun addressing. Partitions and holders are ignored, so the output is one line per physical device — useful for matching a LUN to a device node after a SAN rescan. It prints nothing on a host with no SCSI devices.

```
lsblk -S
```

The equivalent filters for NVMe and virtio backing devices, each also silent when the host has none of that type:

```
lsblk -N
```

```
lsblk -v
```

## lsblk - Identify SSDs and Rotational Disks

The `ROTA` column is the kernel's rotational flag: 1 for spinning disks, 0 for SSDs, NVMe and most virtual disks. Use it to pick which disks get the noop/none scheduler or which are safe to over-provision.

```
lsblk -dno NAME,ROTA
```

Read it alongside model and transport for a usable inventory line:

```
lsblk -d -o NAME,SIZE,ROTA,TRAN,MODEL,SERIAL
```

Note that hypervisors and hardware RAID controllers often report the wrong value, so treat it as a hint rather than ground truth.

## lsblk - Show Permissions and Ownership

Print the owner, group and mode of each device node. This is how to check why a non-root process cannot open a raw device — typically it needs to be in the `disk` group, or a udev rule has not applied.

```
lsblk -m
```

## lsblk - Show Zone Information

Print the zone model and geometry for zoned block devices such as SMR drives and ZNS SSDs. `ZONED` reads `none` on a conventional device and `host-managed` or `host-aware` on a zoned one, in which case the filesystem must support sequential-write zones.

```
lsblk -z
```

## lsblk - Sort and De-Duplicate

Sort by any column. This switches to list output by default, since a sorted tree would break the parent-child ordering.

```
lsblk -x SIZE -o NAME,SIZE,TYPE
```

Keep the tree and sort only the branches by adding `-T`:

```
lsblk -x SIZE -T -o NAME,SIZE,TYPE
```

Collapse duplicate paths to the same device using a column as the key. On multipath hardware the same LUN appears once per path, and `-E WWN` folds those into a single entry:

```
lsblk -E WWN -o NAME,WWN,SIZE
```

`-M` serves the related purpose of grouping the parents of a sub-tree, which makes RAID and multipath sets readable:

```
lsblk -M
```

## lsblk - Find a UUID for fstab

Device names such as `/dev/sdb` are assigned in probe order and can move between boots, so fstab and crypttab entries should reference the filesystem UUID instead.

```
lsblk -dno UUID /dev/nvme0n1p2
```

Build the fstab line directly from it:

```
echo "UUID=$(lsblk -dno UUID /dev/nvme0n1p2) /boot ext4 defaults 0 2"
```

`PARTUUID` identifies the partition rather than the filesystem, and survives a reformat:

```
lsblk -o NAME,PARTN,PARTTYPENAME,PARTUUID,START,SIZE
```

## lsblk - Inspect Another Root Filesystem

Read the sysfs and udev data from a different system root instead of the running one, for example a mounted rescue or chroot target.

```
lsblk --sysroot /mnt/target
```

## lsblk - Relationship to blkid and findmnt

lsblk answers "what devices exist and how are they stacked". It reads sysfs and udev, so it works without root, but the filesystem metadata it prints comes from the udev database and can be stale after a reformat — run `udevadm settle` first if a device was just changed.

blkid is the authoritative source for filesystem type, label and UUID because it probes the device signatures directly. It needs root to read a device it has no cached entry for.

```
blkid /dev/nvme0n1p2
```

findmnt is the authoritative source for mounts, since it reads the kernel mount table rather than udev, and unlike lsblk it shows bind mounts, network filesystems and mount options.

```
findmnt /boot
```

```
findmnt -no SOURCE /
```

The usual division of labour: lsblk to see the topology, blkid to confirm what is actually on a device before formatting it, findmnt to see what is mounted where and with which options.
