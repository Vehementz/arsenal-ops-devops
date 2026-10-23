# Virt

The virt-* tools (virt-install, virt-clone, virt-viewer, virt-top, virt-sysprep, and the libguestfs utilities) create, clone, inspect, and prepare KVM/QEMU virtual machines. They complement `virsh`.

#platform/linux #target/Virtualization #cat/DevOps

% virt, virt-install, virt-clone, virt-viewer, virt-top, libguestfs, kvm, qemu

## Virt - Install a VM from an ISO

Create a new VM and boot the installer from an ISO.

```
virt-install --name <name> --memory <MiB> --vcpus <count> --disk size=<GiB> --cdrom <path/to/file.iso> --os-variant <os-variant>
```

## Virt - Install a VM from a Cloud Image

Create a VM from an existing disk image without running an installer.

```
virt-install --name <name> --memory <MiB> --vcpus <count> --disk <path/to/image.qcow2> --import --os-variant <os-variant> --noautoconsole
```

## Virt - Install a VM Headless

Install with a text console instead of a graphical display.

```
virt-install --name <name> --memory <MiB> --vcpus <count> --disk size=<GiB> --location <url-or-iso> --os-variant <os-variant> --graphics none --extra-args "console=ttyS0"
```

## Virt - Install a VM on a Bridge Network

Attach the VM to a host bridge instead of the default NAT network.

```
virt-install --name <name> --memory <MiB> --vcpus <count> --disk size=<GiB> --cdrom <path/to/file.iso> --network bridge=<bridge> --os-variant <os-variant>
```

## Virt - List OS Variants

Find the correct `--os-variant` value.

```
virt-install --osinfo list
osinfo-query os | grep -i <keyword>
```

## Virt - Clone a VM

Clone a stopped VM, including its disks.

```
virt-clone --original <source-domain> --name <new-name> --auto-clone
```

## Virt - Clone a VM with a Specific Disk Path

Clone a stopped VM and choose the new disk file.

```
virt-clone --original <source-domain> --name <new-name> --file <path/to/new-disk.qcow2>
```

## Virt - Open a VM Display

Open the graphical console of a VM.

```
virt-viewer <domain>
virt-viewer --connect qemu+ssh://<user>@<host>/system <domain>
```

## Virt - Monitor VM Resource Usage

Show a top-like view of CPU, memory, and I/O per VM.

```
virt-top
```

## Virt - Open Virt Manager

Launch the graphical VM manager, locally or against a remote host.

```
virt-manager
virt-manager -c qemu+ssh://<user>@<host>/system
```

## Virt - Prepare a Template with Sysprep

Remove host-specific data (SSH host keys, machine-id, logs) from a stopped VM before using it as a template.

```
virt-sysprep -d <domain>
virt-sysprep -a <path/to/disk.qcow2>
```

## Virt - Inspect a Disk Image

Show the operating system and filesystems found in a disk image.

```
virt-inspector -a <path/to/disk.qcow2>
virt-filesystems -a <path/to/disk.qcow2> --long -h
```

## Virt - Browse and Copy Files in a Disk Image

List a directory, or copy a file out of a stopped VM's disk.

```
virt-ls -d <domain> <path>
virt-cat -d <domain> <path/to/file>
virt-copy-out -d <domain> <path/in/guest> <local-dir>
```

## Virt - Resize a Disk Image

Grow a qcow2 image, then expand a partition inside it into a new image.

```
qemu-img resize <path/to/disk.qcow2> +<size>G
virt-resize --expand /dev/sda1 <path/to/old.qcow2> <path/to/new.qcow2>
```

## Virt - Check Host Virtualization Support

Verify that the host supports hardware virtualization and is ready to run KVM.

```
virt-host-validate
egrep -c '(vmx|svm)' /proc/cpuinfo
```
