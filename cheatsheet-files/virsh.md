# Virsh

Virsh is the command-line interface for managing libvirt virtualization guests (domains), networks, storage pools, and snapshots on KVM/QEMU hosts.

#platform/linux #target/Virtualization #cat/DevOps

% virsh, libvirt, kvm, qemu, virtual machines

## Virsh - List Domains

List running VMs, or all VMs including stopped ones.

```
virsh list
virsh list --all
```

## Virsh - Start a Domain

Start a defined VM.

```
virsh start <domain>
```

## Virsh - Shutdown a Domain

Gracefully shut down a VM via ACPI.

```
virsh shutdown <domain>
```

## Virsh - Force Stop a Domain

Immediately power off a VM (like pulling the plug).

```
virsh destroy <domain>
```

## Virsh - Reboot a Domain

Gracefully reboot a VM.

```
virsh reboot <domain>
```

## Virsh - Suspend and Resume a Domain

Pause a VM in memory, then resume it.

```
virsh suspend <domain>
virsh resume <domain>
```

## Virsh - Autostart a Domain

Start a VM automatically when the host boots, or disable it.

```
virsh autostart <domain>
virsh autostart --disable <domain>
```

## Virsh - Show Domain Info

Display general information, state, and resource usage of a VM.

```
virsh dominfo <domain>
virsh domstate <domain>
virsh domstats <domain>
```

## Virsh - Open a Console

Attach to the serial console of a VM (exit with `Ctrl+]`).

```
virsh console <domain>
```

## Virsh - Get Domain IP Address

Show the IP addresses of a running VM.

```
virsh domifaddr <domain>
```

## Virsh - Edit Domain XML

Edit the XML definition of a VM in your default editor.

```
virsh edit <domain>
```

## Virsh - Dump Domain XML

Print the XML definition of a VM, or save it to a file.

```
virsh dumpxml <domain>
virsh dumpxml <domain> > <domain>.xml
```

## Virsh - Define a Domain from XML

Register a VM from an XML file without starting it.

```
virsh define <file.xml>
```

## Virsh - Undefine a Domain

Remove a VM definition, optionally with its storage and NVRAM.

```
virsh undefine <domain>
virsh undefine <domain> --remove-all-storage --nvram
```

## Virsh - Change Memory and vCPUs

Set the maximum and current memory (in KiB) and vCPU count, applied at next boot.

```
virsh setmaxmem <domain> <size-in-KiB> --config
virsh setmem <domain> <size-in-KiB> --config
virsh setvcpus <domain> <count> --config --maximum
virsh setvcpus <domain> <count> --config
```

## Virsh - Attach a Disk

Attach a disk image to a VM persistently.

```
virsh attach-disk <domain> <path/to/disk.img> <target-dev> --persistent
```

## Virsh - Detach a Disk

Detach a disk from a VM persistently.

```
virsh detach-disk <domain> <target-dev> --persistent
```

## Virsh - Create a Snapshot

Create a snapshot of a VM.

```
virsh snapshot-create-as <domain> --name <snapshot-name> --description "<description>"
```

## Virsh - List Snapshots

List the snapshots of a VM.

```
virsh snapshot-list <domain>
```

## Virsh - Revert to a Snapshot

Restore a VM to a previous snapshot.

```
virsh snapshot-revert <domain> <snapshot-name>
```

## Virsh - Delete a Snapshot

Delete a snapshot of a VM.

```
virsh snapshot-delete <domain> <snapshot-name>
```

## Virsh - List Networks

List active virtual networks, or all of them.

```
virsh net-list
virsh net-list --all
```

## Virsh - Manage a Network

Start a network, enable autostart, or inspect its definition.

```
virsh net-start <network>
virsh net-autostart <network>
virsh net-dumpxml <network>
virsh net-dhcp-leases <network>
```

## Virsh - Storage Pools

List storage pools and the volumes inside a pool.

```
virsh pool-list --all
virsh vol-list <pool>
```

## Virsh - Create a Volume

Create a new qcow2 volume in a storage pool.

```
virsh vol-create-as <pool> <volume-name> <size> --format qcow2
```

## Virsh - Connect to a Remote Host

Run virsh against a remote libvirt daemon over SSH.

```
virsh -c qemu+ssh://<user>@<host>/system list --all
```

## Virsh - Live Migrate a Domain

Migrate a running VM to another host.

```
virsh migrate --live --verbose <domain> qemu+ssh://<user>@<host>/system
```
