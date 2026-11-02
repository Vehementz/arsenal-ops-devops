# pct

pct is the Proxmox VE Container Toolkit. It manages LXC containers on a Proxmox node: create, start, stop, configure, enter, snapshot, and back them up.

#platform/linux #target/Proxmox #cat/Virtualization

% pct, proxmox, lxc, container, virtualization

## pct - List Containers

List all containers on the current node with their status.

```
pct list
```

## pct - Create a Container

Create a container from a template with the given ID, hostname, storage, and network.

```
pct create <vmid> <storage>:vztmpl/<template>.tar.zst --hostname <hostname> --memory <mb> --cores <n> --rootfs <storage>:<size-gb> --net0 name=eth0,bridge=vmbr0,ip=dhcp --password
```

## pct - Start a Container

Start the container with the given ID.

```
pct start <vmid>
```

## pct - Stop a Container

Stop the container immediately.

```
pct stop <vmid>
```

## pct - Shutdown a Container

Cleanly shut down the container.

```
pct shutdown <vmid>
```

## pct - Reboot a Container

Reboot the container.

```
pct reboot <vmid>
```

## pct - Show Container Status

Display the current status of a container.

```
pct status <vmid>
```

## pct - Enter a Container

Open a shell inside the container from the Proxmox host.

```
pct enter <vmid>
```

## pct - Execute a Command in a Container

Run a single command inside the container.

```
pct exec <vmid> -- <command>
```

## pct - Show Container Configuration

Display the configuration of a container.

```
pct config <vmid>
```

## pct - Set Container Options

Change container settings such as memory, cores, or hostname.

```
pct set <vmid> --memory <mb> --cores <n> --hostname <hostname>
```

## pct - Resize Container Disk

Grow the container root filesystem (or another mount point) by the given size.

```
pct resize <vmid> rootfs +<size>G
```

## pct - Push a File to a Container

Copy a file from the host into the container.

```
pct push <vmid> <local-file> <container-path>
```

## pct - Pull a File from a Container

Copy a file from the container to the host.

```
pct pull <vmid> <container-path> <local-file>
```

## pct - Create a Snapshot

Create a snapshot of the container.

```
pct snapshot <vmid> <snapname>
```

## pct - Rollback a Snapshot

Roll the container back to a snapshot.

```
pct rollback <vmid> <snapname>
```

## pct - Delete a Snapshot

Delete a container snapshot.

```
pct delsnapshot <vmid> <snapname>
```

## pct - Clone a Container

Create a new container as a copy of an existing one.

```
pct clone <vmid> <newid> --hostname <hostname> --full
```

## pct - Migrate a Container

Migrate the container to another cluster node.

```
pct migrate <vmid> <target-node> --restart
```

## pct - Mount Container Filesystem

Mount the container root filesystem on the host (container must be stopped).

```
pct mount <vmid>
```

## pct - Unmount Container Filesystem

Unmount a previously mounted container filesystem.

```
pct unmount <vmid>
```

## pct - Destroy a Container

Permanently delete the container and its volumes.

```
pct destroy <vmid> --purge
```

## pct - Backup a Container

Back up a container with vzdump.

```
vzdump <vmid> --storage <storage> --mode snapshot --compress zstd
```

## pct - List Container Templates

Update the template index and list available container templates.

```
pveam update && pveam available
```

## pct - Download a Container Template

Download a template to local storage.

```
pveam download <storage> <template>
```
