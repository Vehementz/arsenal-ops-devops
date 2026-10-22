# NetBird

NetBird is an open-source, WireGuard-based overlay network that connects machines into a secure peer-to-peer private network with centralized access control. The `netbird` CLI manages the client agent on each peer.

#platform/multiple #target/Network #cat/VPN

% netbird, wireguard, vpn, mesh, zero-trust, overlay

## NetBird - Install Client

Install the NetBird client with the official install script (Linux/macOS).

```
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

## NetBird - Connect

Start the client and connect to the network (opens SSO login in a browser on first run).

```
netbird up
```

## NetBird - Connect With Setup Key

Connect a headless peer non-interactively using a setup key.

```
netbird up --setup-key <setup-key>
```

## NetBird - Connect To Self-Hosted Server

Connect to a self-hosted management server instead of NetBird Cloud.

```
netbird up --management-url https://<netbird-domain>:443 --setup-key <setup-key>
```

## NetBird - Disconnect

Disconnect from the network and stop the tunnel.

```
netbird down
```

## NetBird - Show Status

Show the connection status of the local peer.

```
netbird status
```

### NetBird - Show Detailed Status

Show detailed status including every peer, connection type (P2P/relayed) and latency.

```
netbird status -d
```

## NetBird - Login

Log in to the management server without bringing the tunnel up.

```
netbird login
```

## NetBird - Logout

Log out and remove the peer's login from the management server.

```
netbird logout
```

## NetBird - List Networks

List network routes/resources available to this peer.

```
netbird networks list
```

## NetBird - Select Networks

Select which network routes this peer should use.

```
netbird networks select <network-id>
```

## NetBird - Install Service

Install NetBird as a system service and start it.

```
sudo netbird service install
sudo netbird service start
```

## NetBird - Stop Service

Stop the NetBird system service.

```
sudo netbird service stop
```

## NetBird - Uninstall Service

Remove the NetBird system service.

```
sudo netbird service uninstall
```

## NetBird - SSH To Peer

Open an SSH session to a peer through NetBird (requires SSH enabled on the target peer).

```
netbird ssh <user>@<peer-ip-or-name>
```

## NetBird - Enable SSH Server

Connect and allow other peers to SSH into this machine through NetBird.

```
netbird up --allow-server-ssh
```

## NetBird - Create Debug Bundle

Generate an anonymized debug bundle for troubleshooting.

```
netbird debug bundle --anonymize
```

## NetBird - Show Version

Show the installed client version.

```
netbird version
```

## NetBird - Run In Docker

Run the NetBird client as a container with a setup key.

```
docker run --rm -d --name netbird --cap-add=NET_ADMIN -e NB_SETUP_KEY=<setup-key> -v netbird-client:/etc/netbird netbirdio/netbird:latest
```
