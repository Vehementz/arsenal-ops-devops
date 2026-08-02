# lvm

LVM (Logical Volume Manager) puts an indirection layer between disks and filesystems: physical volumes (PVs) are whole disks or partitions handed to LVM, a volume group (VG) pools the space of one or more PVs, and logical volumes (LVs) are carved out of that pool and carry the filesystem. Because an LV is not tied to one disk, space can be added to a running server by adding a disk to the VG and growing the LV, which is why it is the default layout on most on-premise Linux installs.

#platform/multiple #target/Linux #cat/Storage

% lvm, logical volumes, storage, disks, pvs, vgs, lvs, lvcreate, lvextend, snapshots, thin provisioning, resize2fs

## lvm - Check Free Space Before You Start

Every resize is limited by the free extents left in the volume group, so read that number first. If it is zero, no LV can grow until a disk is added to the VG.

```
vgs
```

Show the free space explicitly, along with the extent size that all allocations are rounded to:

```
vgs -o vg_name,vg_size,vg_free,vg_extent_size,vg_free_count
```

See the whole stack, disk to LV, without needing root:

```
lsblk
```

## lvm - Inspect Physical Volumes

List the devices LVM has claimed, which VG each belongs to, and how much of each is still unallocated.

```
pvs
```

Print the long form for one device, including the extent count and the PV UUID:

```
pvdisplay /dev/<device>
```

## lvm - Inspect Volume Groups

List the volume groups with their size, free space, and the number of PVs and LVs they hold.

```
vgs
```

Print the long form for one group:

```
vgdisplay <vg>
```

## lvm - Inspect Logical Volumes

List the logical volumes with their size and the volume group they live in.

```
lvs
```

Print the long form, including the LV path and its current activation state:

```
lvdisplay <vg>/<lv>
```

Include internal and hidden volumes, such as thin pool data and metadata sub-volumes:

```
lvs -a
```

## lvm - Select Report Columns

`pvs`, `vgs` and `lvs` share a reporting engine. A leading `+` in `-o` appends columns to the defaults instead of replacing them, which is the quickest way to answer a specific question without memorising a full field list.

Show which physical devices back each LV, which is what you need before replacing a disk:

```
lvs -o +devices
```

Append free space to the VG report:

```
vgs -o +vg_free
```

Report in fixed units rather than the auto-scaled default, so numbers can be compared or parsed:

```
lvs -o lv_name,lv_size --units g
```

List every available field for a command:

```
lvs -o help
```

## lvm - Create a Physical Volume

Write an LVM label onto a disk or partition so it can be added to a volume group. This wipes any existing filesystem signature on the device.

```
pvcreate /dev/<device>
```

Initialise several devices in one call:

```
pvcreate /dev/sdb /dev/sdc
```

## lvm - Create a Volume Group

Create a pool from one or more physical volumes. `vgcreate` will run `pvcreate` implicitly on devices that are not yet initialised.

```
vgcreate <vg> /dev/<device>
```

Set a non-default physical extent size. This is the allocation granularity for every LV in the group and is difficult to change afterwards:

```
vgcreate -s 16M <vg> /dev/<device>
```

## lvm - Add a Disk to an Existing Volume Group

This is the core "we ran out of space" workflow: add the new disk to the VG, then grow the LV into the space it brings. Nothing has to be unmounted and no data moves.

```
pvcreate /dev/<new-device>
vgextend <vg> /dev/<new-device>
```

Confirm the free space arrived before extending anything:

```
vgs <vg>
```

## lvm - Create a Logical Volume by Size

Allocate a fixed amount of space and give the volume a name.

```
lvcreate -L 20G -n <lv> <vg>
```

Then put a filesystem on it and mount it:

```
mkfs.ext4 /dev/<vg>/<lv>
mount /dev/<vg>/<lv> /mnt/<mountpoint>
```

## lvm - Create a Logical Volume by Percentage

`-l` takes a number of extents, optionally with a percentage suffix, which avoids arithmetic and avoids leaving a few unusable extents behind. `%FREE` is the free space remaining in the VG; `%VG` is the total size of the VG.

Consume everything still free in the group:

```
lvcreate -l 100%FREE -n <lv> <vg>
```

Take half of the group's total size:

```
lvcreate -l 50%VG -n <lv> <vg>
```

Take a fixed number of extents:

```
lvcreate -l 512 -n <lv> <vg>
```

## lvm - Find the Device Path of a Volume

LVM exposes each active LV twice. `/dev/<vg>/<lv>` is a symlink created on activation and is the name to use in scripts and `/etc/fstab`. `/dev/mapper/<vg>-<lv>` is the device-mapper node the symlink points at, and is what `lsblk`, `df` and `mount` report; literal hyphens in a VG or LV name are doubled there.

```
ls -l /dev/<vg>/<lv>
ls -l /dev/mapper/
```

Prefer the UUID in `/etc/fstab` so a later rename does not break the boot:

```
blkid /dev/<vg>/<lv>
```

## lvm - Extend a Logical Volume and Grow the Filesystem

Growing an LV only enlarges the block device; the filesystem inside it still believes it is the old size until it is resized too. `-r` resizes the filesystem in the same command via `fsadm`, which is the safe default because it removes the chance of forgetting the second step.

Add 10 GiB and grow the filesystem with it:

```
lvextend -r -L +10G <vg>/<lv>
```

Grow into all remaining free space in the VG:

```
lvextend -r -l +100%FREE <vg>/<lv>
```

Set an absolute new size rather than an increment (note the missing `+`):

```
lvextend -r -L 100G <vg>/<lv>
```

If `-r` was omitted, grow the filesystem afterwards. Both of these work on a mounted filesystem, so no downtime is needed:

```
resize2fs /dev/<vg>/<lv>
xfs_growfs /mnt/<mountpoint>
```

Growing is safe and online for both ext4 and XFS. XFS can only ever grow — there is no shrink tool for it, so an XFS volume that is too large can only be reclaimed by backing up, recreating and restoring.

## lvm - Shrink an ext4 Logical Volume

Shrinking runs in the opposite order to growing, and getting the order wrong destroys data: `lvreduce` truncates the block device blindly, so the filesystem must be made smaller *first*. Only ext2/3/4 can be shrunk; XFS cannot. Take a backup before starting.

```
umount /mnt/<mountpoint>
e2fsck -f /dev/<vg>/<lv>
resize2fs /dev/<vg>/<lv> 40G
lvreduce -L 40G <vg>/<lv>
mount /dev/<vg>/<lv> /mnt/<mountpoint>
```

`e2fsck -f` is mandatory: `resize2fs` refuses to shrink a filesystem that has not been forced through a clean check. Shrink the filesystem to a value slightly below the target LV size, or let `lvreduce -r` drive `fsadm` and keep the two in step for you:

```
lvreduce -r -L 40G <vg>/<lv>
```

Preview the operation without touching anything:

```
lvreduce -t -L 40G <vg>/<lv>
```

## lvm - Rename a Logical Volume

Renaming changes the `/dev/<vg>/<lv>` symlink and the device-mapper node, so anything referring to the volume by path — `/etc/fstab`, unit files, container mounts — breaks unless it uses the UUID.

```
lvrename <vg> <old-lv> <new-lv>
```

Equivalent form using full paths:

```
lvrename <vg>/<old-lv> <vg>/<new-lv>
```

## lvm - Create a Snapshot

A copy-on-write snapshot gives a frozen view of an LV while the origin stays in use, which is how to take a consistent backup or a rollback point before a risky upgrade. The size given to the snapshot is not a copy of the data — it is the space reserved for blocks that change while the snapshot exists.

```
lvcreate -s -L 5G -n <lv>-snap <vg>/<lv>
```

Mount it read-only to back it up:

```
mount -o ro /dev/<vg>/<lv>-snap /mnt/snap
```

Size it against expected write volume; roughly 20% of the origin is a common starting point. Watch how full it is, because a COW snapshot that fills up is invalidated by the kernel and silently becomes useless — the origin is unharmed, but the snapshot's contents are gone:

```
lvs -o lv_name,lv_size,data_percent,lv_attr <vg>
```

An `I` in the fifth character of the `lv_attr` column marks an invalid snapshot. Extend a snapshot that is filling faster than expected:

```
lvextend -L +5G <vg>/<lv>-snap
```

Discard a snapshot once the backup is done, since leaving it around costs write performance on the origin:

```
lvremove <vg>/<lv>-snap
```

## lvm - Merge a Snapshot Back Into Its Origin

Merging rolls the origin back to the state captured at snapshot time and then removes the snapshot. If both the origin and the snapshot are closed the merge starts immediately; otherwise it is deferred until the next activation, which for a root filesystem means the next reboot.

```
lvconvert --merge <vg>/<lv>-snap
```

Close the origin first if you want the merge to run now:

```
umount /mnt/<mountpoint>
lvchange -an <vg>/<lv>
lvconvert --merge <vg>/<lv>-snap
lvchange -ay <vg>/<lv>
```

## lvm - Create a Thin Pool and Thin Volumes

Thin volumes allocate blocks from a shared pool only as they are written, so the sum of the volumes may exceed the pool size. This is useful for many similarly sized volumes with unpredictable fill rates, at the cost of a real risk of over-commitment.

Create the pool, then create thin volumes with a virtual size inside it:

```
lvcreate --type thin-pool -L 200G -n <pool> <vg>
lvcreate -V 50G --thinpool <vg>/<pool> -n <lv> <vg>
```

Thin snapshots take no size argument and consume no space until blocks diverge, which makes them cheap enough to take frequently:

```
lvcreate -s -n <lv>-snap <vg>/<lv>
```

## lvm - Monitor Thin Pool Usage

A thin pool that runs out of data or metadata space blocks or errors I/O on every volume inside it, so the pool — not the volumes — is the number to alert on.

```
lvs -o lv_name,lv_size,data_percent,metadata_percent <vg>/<pool>
```

Metadata exhaustion is the failure mode people forget; extend it separately from the data area:

```
lvextend --poolmetadatasize +1G <vg>/<pool>
lvextend -L +100G <vg>/<pool>
```

`dmeventd` (the `lvm2-monitor` service) extends monitored pools automatically once they cross `thin_pool_autoextend_threshold` in `lvm.conf`. If that service is not running, no automatic extension happens at all.

## lvm - Replace a Failing Disk

`pvmove` relocates the allocated extents off one PV onto the remaining free space in the group. It runs online, so a dying disk can be evacuated without downtime, and it restarts from its last checkpoint if it is interrupted.

Check which volumes are on the device first:

```
pvs -o +pv_used
lvs -o +devices
```

Move everything off it, letting LVM pick destinations:

```
pvmove /dev/<old-device>
```

Move to a specific destination PV instead:

```
pvmove /dev/<old-device> /dev/<new-device>
```

Move only the extents belonging to one LV:

```
pvmove -n <vg>/<lv> /dev/<old-device>
```

Run it detached in the background, or report progress at regular intervals, since a full disk can take hours:

```
pvmove -b /dev/<old-device>
pvmove -i 10 /dev/<old-device>
```

Abort a move in progress:

```
pvmove --abort
```

Once the PV reports zero used extents, drop it from the group and unlabel it:

```
vgreduce <vg> /dev/<old-device>
pvremove /dev/<old-device>
```

## lvm - Remove Volumes and Reclaim Devices

Removal runs top-down: the LV first, then the VG, then the PV labels. Each step destroys data and none of them are undoable.

```
umount /mnt/<mountpoint>
lvremove <vg>/<lv>
vgremove <vg>
pvremove /dev/<device>
```

`lvremove` refuses to remove an open volume, which is the safety net against deleting something still mounted. Check what is holding it before reaching for `-f`:

```
lsof /mnt/<mountpoint>
```

## lvm - Activate and Deactivate Volumes

An inactive LV has no device node and cannot be opened. Deactivating is the correct way to take a volume offline before maintenance, and activating is what is needed after importing a group from another machine.

Deactivate and reactivate a single volume:

```
lvchange -an <vg>/<lv>
lvchange -ay <vg>/<lv>
```

Activate or deactivate every volume in a group:

```
vgchange -ay <vg>
vgchange -an <vg>
```

Mark a volume read-only, which is useful when mounting a recovered filesystem you do not want to modify:

```
lvchange -pr <vg>/<lv>
```

## lvm - Rescan After Attaching Disks

A hot-plugged disk that already carries LVM metadata will not show up until LVM re-reads the devices and updates its cache.

```
pvscan --cache
vgscan
lvscan
```

Scan and autoactivate any volume groups that became complete as a result:

```
pvscan --cache -a ay
```

## lvm - Back Up and Restore LVM Metadata

LVM writes a copy of the VG metadata to `/etc/lvm/backup/<vg>` after every change and keeps the previous versions in `/etc/lvm/archive`. This is the layout only — it holds no file data — but it is what lets you undo a mistaken `lvremove` or `vgreduce` if nothing has overwritten the extents yet.

Take an explicit backup before a risky change:

```
vgcfgbackup <vg>
```

List the backup and archive files LVM holds for the group. This only lists them; it restores nothing:

```
vgcfgrestore -l <vg>
```

Roll the VG back to a specific archive file, using a path taken from that listing:

```
vgcfgrestore -f /etc/lvm/archive/<archive-file>.vg <vg>
```

Restore the most recent backup when no file is named:

```
vgcfgrestore <vg>
```

Restoring a VG that contains thin pools is not reversible — thin metadata changes cannot be rolled back and data loss is likely, so LVM requires `--force` in that case. Back up `/etc/lvm` along with the rest of the system.

## lvm - Inspect Extent Layout

When allocation fails despite apparently free space, or a volume needs to be pinned to particular disks, look at the extent maps. `-m` shows which physical extents on which device back each segment.

```
lvdisplay -m <vg>/<lv>
```

Show the same mapping from the device side, including free ranges:

```
pvdisplay -m /dev/<device>
```

Report per-segment rather than per-volume:

```
lvs --segments -o +devices
```
