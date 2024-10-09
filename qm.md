# QM (Qemu Manager) Command Reference

QM is the command-line tool used to manage virtual machines (VMs) in Proxmox Virtual Environment (PVE). It allows users to create, configure, start, stop, and monitor virtual machines running on PVE.

#platform/multiple #target/Proxmox #cat/Virtualization

% proxmox, qemu, VM management, virtualization

## QM - List VMs

List all virtual machines on the Proxmox node.

```
qm list
```

## QM - Create a Virtual Machine

Create or restore a virtual machine with the specified `VM_ID`.

```
qm create <VM_ID>
```

## QM - Start a Virtual Machine

Start a virtual machine with the specified `VM_ID`.

```
qm start <VM_ID>
```

## QM - Suspend a Virtual Machine

Suspend a running virtual machine with the specified `VM_ID`.

```
qm suspend <VM_ID>
```

## QM - Shutdown a Virtual Machine

Shutdown a virtual machine gracefully with the specified `VM_ID`.

```
qm shutdown <VM_ID>
```

## QM - Reboot a Virtual Machine

Reboot a virtual machine with the specified `VM_ID`.

```
qm reboot <VM_ID>
```

## QM - Reset a Virtual Machine

Reset a virtual machine with the specified `VM_ID`.

```
qm reset <VM_ID>
```

## QM - Stop a Virtual Machine

Force stop a virtual machine with the specified `VM_ID`.

```
qm stop <VM_ID>
```

## QM - Destroy a Virtual Machine

Destroy the virtual machine and all of its associated volumes with the specified `VM_ID`.

```
qm destroy <VM_ID>
```

## QM - Monitor a Virtual Machine

Enter the Qemu Monitor interface for the virtual machine with the specified `VM_ID`.

```
qm monitor <VM_ID>
```

## QM - Get Pending VM Configuration

Display the virtual machine configuration with both current and pending values for the specified `VM_ID`.

```
qm pending <VM_ID>
```

## QM - Send Key Event to Virtual Machine

Send a key event to the virtual machine with the specified `VM_ID` and key event options.

```
qm sendkey <VM_ID> <YOUR_KEY_EVENT> [OPTIONS]
```

## QM - Show Command Line of a Virtual Machine

Show the command line used to start the virtual machine for the specified `VM_ID` (useful for debugging).

```
qm showcmd <VM_ID> [OPTIONS]
```

## QM - Unlock a Virtual Machine

Unlock the virtual machine with the specified `VM_ID`.

```
qm unlock <VM_ID>
```

## QM - Clone a Virtual Machine

Clone a virtual machine using the specified `VM_ID` and create a new one with `NEW_VM_ID`.

```
qm clone <VM_ID> <NEW_VM_ID>
```

## QM - Migrate a Virtual Machine

Migrate a virtual machine with the specified `VM_ID` to a target node `TARGET_NODE`.

```
qm migrate <VM_ID> <TARGET_NODE>
```

## QM - Show VM Status

Show the current status of the virtual machine with the specified `VM_ID`.

```
qm status <VM_ID>
```

## QM - Clean up VM Resources

Clean up resources for the specified `VM_ID` using clean shutdown or guest requested options.

```
qm cleanup <VM_ID> <CLEAN_SHUTDOWN> <GUEST_REQUESTED>
```

## QM - Create a VM Template

Create a virtual machine template with the specified `VM_ID` and additional options.

```
qm template <VM_ID> [OPTIONS]
```

## QM - Set VM Options

Set or modify virtual machine options for the specified `VM_ID`.

```
qm set <VM_ID> [OPTIONS]
```

## QM - CloudInit Dump

Get the automatically generated CloudInit configuration for the virtual machine with the specified `VM_ID` and `VM_TYPE`.

```
qm cloudinit dump <VM_ID> <VM_TYPE>
```

## QM - CloudInit Pending Configuration

Get the CloudInit configuration for the virtual machine with both current and pending values for the specified `VM_ID`.

```
qm cloudinit pending <VM_ID>
```

## QM - CloudInit Update

Regenerate and change the CloudInit configuration drive for the virtual machine with the specified `VM_ID`.

```
qm cloudinit update <VM_ID>
```

## QM - Import External Disk Image

Import an external disk image as an unused disk in the virtual machine with the specified `VM_ID`. You need to provide the `TARGET_SOURCE` and `TARGET_STORAGE`.

```
qm disk import <VM_ID> <TARGET_SOURCE> <TARGET_STORAGE>
```

## QM - Move Disk Volume

Move the disk volume associated with the virtual machine to different storage or a different virtual machine. Specify the `VM_ID`, the `VM_DISK`, and optional `STORAGE` or other options.

```
qm disk move <VM_ID> <VM_DISK> [STORAGE] [OPTIONS]
```

## QM - Rescan All Storages

Rescan all storages and update disk sizes and unused disk images.

```
qm disk rescan [OPTIONS]
```

## QM - Resize Disk Volume

Extend the disk volume size for a virtual machine with the specified `VM_ID`, `VM_DISK`, and `SIZE`.

```
qm disk resize <VM_ID> <VM_DISK> <SIZE> [OPTIONS]
```

## QM - Unlink/Delete Disk Images

Unlink or delete disk images for the virtual machine with the specified `VM_ID`. Use `--IDLIST STRING` to specify the list of disks to unlink.

```
qm disk unlink <VM_ID> --IDLIST <STRING> [OPTIONS]
```

## QM - Rescan Volumes

Rescan volumes for the virtual machine.

```
qm rescan
```

## QM - List VM Snapshots

List all snapshots for the virtual machine with the specified `VM_ID`.

```
qm listsnapshot <VM_ID>
```

## QM - Create VM Snapshot

Take a snapshot of the virtual machine with the specified `VM_ID` and `SNAPNAME`.

```
qm snapshot <VM_ID> <SNAPNAME>
```

## QM - Delete VM Snapshot

Delete a snapshot of the virtual machine with the specified `VM_ID` and `SNAPNAME`.

```
qm delsnapshot <VM_ID> <SNAPNAME>
```

## QM - Rollback to VM Snapshot

Rollback the virtual machine to the specified snapshot `SNAPNAME` for the virtual machine with the specified `VM_ID`.

```
qm rollback <VM_ID> <SNAPNAME>
```

## QM - Open VM Terminal

Open a terminal using a serial device for the virtual machine with the specified `VM_ID`.

```
qm terminal <VM_ID> [OPTIONS]
```

## QM - Proxy VM VNC Traffic

Proxy VM VNC traffic to stdin/stdout for the virtual machine with the specified `VM_ID`.

```
qm vncproxy <VM_ID>
```

## QM - Execute Guest Agent Commands

Execute Qemu Guest Agent commands on the virtual machine with the specified `VM_ID` and `COMMAND`.

```
qm guest cmd <VM_ID> <COMMAND>
```

## QM - Execute Command via Guest Agent

Execute a specific command in the guest virtual machine using the Qemu Guest Agent for the virtual machine with the specified `VM_ID`. Additional `EXTRA-ARGS` and `OPTIONS` can be provided.

```
qm guest exec <VM_ID> [EXTRA-ARGS] [OPTIONS]
```

## QM - Get Guest Execution Status

Get the status of a command that was started by the guest agent, identified by its process ID (`PID`), for the virtual machine with the specified `VM_ID`.

```
qm guest exec-status <VM_ID> <PID>
```

## QM - Set Guest User Password

Set the password for the specified `USERNAME` in the guest virtual machine with the specified `VM_ID`.

```
qm guest passwd <VM_ID> <USERNAME> [OPTIONS]
```