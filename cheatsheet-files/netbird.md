# NetBird

NetBird is an open-source WireGuard-based mesh VPN that connects machines into a secure private network with SSO, access control, and no manual firewall configuration.

#platform/multiple #target/Networking #cat/VPN

% netbird, vpn, wireguard, mesh network, zero trust

## NetBird - Install on Linux

Install the NetBird client using the official install script.

```
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

## NetBird - Check Version

Verify that NetBird has been installed correctly.

```
netbird version
```

## NetBird - Connect to the Network

Start the client and authenticate through the SSO login flow.

```
netbird up
```

## NetBird - Connect with a Setup Key

Register a peer non-interactively using a setup key, useful for servers and CI.

```
netbird up --setup-key <setup-key>
```

## NetBird - Connect to a Self-Hosted Management Server

Point the client at a self-hosted management server.

```
netbird up --management-url <management-url>
```

## NetBird - Disconnect from the Network

Bring the connection down.

```
netbird down
```

## NetBird - Show Status

Display the connection state, the peers, and their connection types.

```
netbird status
```

Show detailed information for every peer.

```
netbird status -d
```

## NetBird - Log Out

Deregister this peer from the network and remove its local login.

```
netbird deregister
```

## NetBird - Manage the Service

Install, start, stop, and restart the NetBird system service.

```
netbird service install
netbird service start
netbird service stop
netbird service restart
```

## NetBird - Enable SSH Server

Allow other peers to connect to this machine through NetBird SSH.

```
netbird up --allow-server-ssh
```

## NetBird - List Networks

List the routed networks available to this peer.

```
netbird networks list
```

## NetBird - Select a Network

Enable a routed network on this peer.

```
netbird networks select <network-id>
```

## NetBird - Deselect a Network

Disable a routed network on this peer.

```
netbird networks deselect <network-id>
```

## NetBird - Set Log Level

Change the client log level for debugging.

```
netbird debug log level debug
```

## NetBird - Create a Debug Bundle

Collect logs and state into a bundle for troubleshooting.

```
netbird debug bundle
```
