# NetBird

NetBird is a WireGuard-based overlay network that connects machines and services into a secure private mesh with SSO, access policies, and a management dashboard.

#platform/multiple #target/Networking #cat/VPN

% netbird, vpn, wireguard, mesh network, overlay network

## NetBird - Install on Linux

Install the NetBird client using the official install script.

```
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

## NetBird - Install the Service

Install and start the NetBird daemon as a system service.

```
sudo netbird service install
sudo netbird service start
```

## NetBird - Connect with SSO Login

Log in via the browser-based SSO flow and bring the connection up.

```
netbird up
```

## NetBird - Connect with a Setup Key

Register a peer non-interactively using a setup key, useful for servers and CI.

```
netbird up --setup-key <setup-key>
```

## NetBird - Connect to a Self-Hosted Management Server

Connect the peer to your own management server.

```
netbird up --management-url <https://netbird.example.com:33073>
```

## NetBird - Set a Custom Hostname

Register the peer with a specific hostname.

```
netbird up --hostname <hostname>
```

## NetBird - Disconnect

Bring the connection down without removing the peer registration.

```
netbird down
```

## NetBird - Show Status

Show connection state, management and signal status, and the local NetBird IP.

```
netbird status
```

### NetBird - Show Detailed Status

Include details about every peer, such as connection type, latency, and routes.

```
netbird status --detail
```

## NetBird - Log Out

Deregister this peer from the account and remove its local login state.

```
netbird logout
```

## NetBird - Show Version

Print the installed client version.

```
netbird version
```

## NetBird - List Networks and Routes

List the networks available to this peer.

```
netbird networks list
```

### NetBird - Select a Network

Enable a network route on this peer.

```
netbird networks select <network-id>
```

### NetBird - Deselect a Network

Disable a network route on this peer.

```
netbird networks deselect <network-id>
```

## NetBird - Set Log Level

Change the daemon log level at runtime.

```
netbird debug log level <debug|info|warn|error>
```

## NetBird - Create a Debug Bundle

Collect logs and diagnostic information to share with support.

```
netbird debug bundle
```

## NetBird - Service Management

Control the NetBird system service.

```
sudo netbird service start
sudo netbird service stop
sudo netbird service restart
sudo netbird service uninstall
```

## NetBird - View Service Logs

Follow the NetBird daemon logs through systemd.

```
journalctl -u netbird -f
```

## NetBird - Run in Docker

Run the NetBird client in a container with the capabilities needed to create the WireGuard interface.

```
docker run -d --name netbird --cap-add=NET_ADMIN --cap-add=SYS_ADMIN --cap-add=SYS_RESOURCE -e NB_SETUP_KEY=<setup-key> -v netbird-client:/etc/netbird netbirdio/netbird:latest
```
