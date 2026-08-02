# ssh

ssh is the OpenSSH client for logging in to a remote machine and executing commands on it over an encrypted channel. Together with its companion tools — ssh-keygen, ssh-copy-id, ssh-agent, ssh-add, scp, sftp and ssh-keyscan — it is the transport underneath most on-premise automation, file transfer and remote debugging.

#platform/multiple #target/Linux #cat/RemoteAccess

% ssh, remote access, tunneling, keys, openssh, scp, sftp, port forwarding, jump host, agent

## ssh - Connect to a Host

Open an interactive shell on a remote machine. Without an explicit user, ssh uses the local username, which is rarely what you want on a server fleet.

```
ssh ops@server1.example.com
```

Connect on a non-standard port. Note the capital `-p`; scp and sftp use `-P` for the same thing, which is a common source of typos.

```
ssh -p 2222 ops@server1.example.com
```

Use a specific private key instead of the default identities. Pair it with `IdentitiesOnly=yes` when the agent holds many keys, otherwise ssh may offer the wrong ones first and hit the server's `MaxAuthTries` limit before reaching the right key.

```
ssh -i ~/.ssh/id_ed25519_ops -o IdentitiesOnly=yes ops@server1.example.com
```

Print the version of the local client, which determines which options and defaults apply:

```
ssh -V
```

## ssh - Run a Single Remote Command

Append a command to run it and exit instead of opening a shell. Everything after the destination is passed to the remote login shell, so quote anything you want expanded remotely rather than locally.

```
ssh ops@server1.example.com 'systemctl is-active nginx'
```

Force a pty for commands that insist on a terminal, such as `sudo` with password prompts or anything using a pager:

```
ssh -t ops@server1.example.com 'sudo journalctl -u nginx -n 50'
```

Pipe a local script to a remote shell. This runs the script without copying it to disk on the target.

```
ssh ops@server1.example.com 'bash -s' < ./bootstrap.sh
```

Stream a remote file into a local pipeline:

```
ssh ops@server1.example.com 'cat /var/log/syslog' | grep -i error
```

## ssh - Generate a Key Pair

Create an Ed25519 key. It is the default recommendation: short, fast, and with no key-size decision to get wrong. The `-C` comment is free text that ends up in the public key and in `authorized_keys`, so use it to record who and which machine the key belongs to.

```
ssh-keygen -t ed25519 -C "ops@workstation-01"
```

Write the key to a named file rather than the default `~/.ssh/id_ed25519`. Use this whenever a key is scoped to one environment, so a compromised laptop key does not also unlock production.

```
ssh-keygen -t ed25519 -C "deploy@ci" -f ~/.ssh/id_ed25519_deploy
```

Generate a key with no passphrase for unattended use, such as a CI runner or a backup job. The empty `-N ''` makes it non-interactive, and the key must then be protected by file permissions and by restrictions in `authorized_keys`.

```
ssh-keygen -t ed25519 -f ./id_ed25519_backup -N '' -C "backup-job"
```

Generate RSA only when a legacy device or appliance cannot handle Ed25519. Anything under 3072 bits is not worth deploying.

```
ssh-keygen -t rsa -b 4096 -C "ops@workstation-01"
```

## ssh - Change a Key Passphrase or Comment

Add, change, or remove the passphrase on an existing private key without regenerating it, so the corresponding public key stays valid everywhere it is already installed.

```
ssh-keygen -p -f ~/.ssh/id_ed25519
```

Do it non-interactively, for example when rotating a passphrase from a script:

```
ssh-keygen -p -f ~/.ssh/id_ed25519 -P 'old passphrase' -N 'new passphrase'
```

Rewrite only the comment, which is useful when a key was generated with a misleading default like `user@hostname`:

```
ssh-keygen -c -C "ops@workstation-01" -f ~/.ssh/id_ed25519
```

Regenerate the public key from a private key whose `.pub` file was lost:

```
ssh-keygen -y -f ~/.ssh/id_ed25519 > ~/.ssh/id_ed25519.pub
```

## ssh - Install a Public Key on a Server

Append a public key to the remote account's `authorized_keys`, creating `~/.ssh` with the right permissions if it is missing. This is the correct way to bootstrap key access while you still have password access.

```
ssh-copy-id -i ~/.ssh/id_ed25519.pub ops@server1.example.com
```

Check what it would do without changing anything on the target:

```
ssh-copy-id -n -i ~/.ssh/id_ed25519.pub ops@server1.example.com
```

Do the same by hand when ssh-copy-id is not installed on the workstation. The `umask` and `mkdir -p` matter: sshd refuses a group- or world-writable `~/.ssh` under the default `StrictModes yes`.

```
cat ~/.ssh/id_ed25519.pub | ssh ops@server1.example.com 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys'
```

Verify afterwards that the key is the only one present and that nothing unexpected was added:

```
ssh ops@server1.example.com 'cat ~/.ssh/authorized_keys'
```

## ssh - Inspect and Convert a Key

Print the fingerprint of a key. This is what you compare against the fingerprint shown on first connection, or against an inventory of authorised keys.

```
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

Fingerprints are SHA256 by default. Older systems and some network appliances still display MD5, so ask for that format when comparing against them.

```
ssh-keygen -lf ~/.ssh/id_ed25519.pub -E md5
```

Show the ASCII art randomart alongside the fingerprint, which is easier to compare visually over a video call than a base64 string:

```
ssh-keygen -lvf ~/.ssh/id_ed25519.pub
```

Export a public key to the RFC4716 format used by some commercial SSH servers:

```
ssh-keygen -e -f ~/.ssh/id_ed25519.pub -m RFC4716
```

Import an RFC4716 key back into OpenSSH format so it can be pasted into `authorized_keys`:

```
ssh-keygen -i -f foreign_key.pub -m RFC4716
```

List the key and algorithm names the local client actually supports, which settles arguments about whether an old cipher is still available:

```
ssh -Q key
```

## ssh - Write a Client Config File

`~/.ssh/config` removes almost all repeated typing and, more importantly, makes connection settings reviewable in one place. A `Host` block names an alias; `HostName` is the address actually dialled.

```
Host web1
    HostName 10.20.0.11
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519_deploy
    IdentitiesOnly yes
```

With that in place, the whole connection collapses to the alias, and so do scp, sftp, rsync and anything else that shells out to ssh:

```
ssh web1
```

Options are also settable per-invocation with `-o`, using exactly the same keyword names as the config file. This is how you test a setting before committing it to the file.

```
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new web1
```

Point at an alternative config file entirely, for example one checked into a repository for a specific environment:

```
ssh -F ./ops/ssh_config web1
```

## ssh - Match Multiple Hosts with Patterns

`Host` accepts glob patterns, so a whole subnet or naming convention can share one block. The first value found for each keyword wins, so put specific blocks above general ones.

```
Host *.internal
    User deploy
    IdentityFile ~/.ssh/id_ed25519_deploy

Host *
    ServerAliveInterval 30
    AddKeysToAgent yes
    HashKnownHosts yes
```

Negate a pattern to carve an exception out of a wildcard:

```
Host *.internal !jump.internal
    ProxyJump jump.internal
```

Use `Match` when the condition is not just the hostname — for instance applying settings only when connecting as a particular user:

```
Match user root
    LogLevel VERBOSE
```

## ssh - Split the Config with Include

`Include` pulls in other files, which lets you keep per-customer or per-environment blocks in separate files and generate them from inventory. Relative paths are resolved against `~/.ssh` in a user config, so keep the fragments there.

```
Include conf.d/*.conf
```

The included files use exactly the same syntax:

```
Host db-*
    User dba
    ProxyJump bastion
```

Because wildcards are expanded in lexical order and the first match wins, name the fragments so ordering is explicit:

```
ls ~/.ssh/conf.d/
```

## ssh - Check What the Config Resolves To

`-G` prints the fully resolved configuration for a destination after evaluating every `Host`, `Match` and `Include`, then exits without connecting. This is the fastest way to find out why a block is not taking effect.

```
ssh -G web1
```

Check one keyword rather than reading all of it:

```
ssh -G web1 | grep -i proxyjump
```

Confirm the identity files and user that would actually be offered:

```
ssh -G web1 | grep -iE '^(user|hostname|port|identityfile|identitiesonly) '
```

## ssh - Connect Through a Jump Host

`-J` connects to the bastion first and forwards a TCP connection to the final target from there. The target is authenticated end-to-end by your client, so the bastion never sees your session traffic or your private key.

```
ssh -J ops@bastion.example.com deploy@10.20.0.11
```

Chain several hops by separating them with commas:

```
ssh -J ops@bastion1.example.com,ops@bastion2.example.com deploy@10.20.0.11
```

Command-line options apply to the final destination, not to the jump hosts, so encode the jump path in the config instead. This form is what you want in practice, because scp, sftp and rsync then inherit it.

```
Host bastion
    HostName bastion.example.com
    User ops

Host 10.20.0.*
    User deploy
    ProxyJump bastion
```

Use `-W` when you need a raw forwarded stream rather than a session, which is the mechanism `ProxyJump` is built on:

```
ssh -W 10.20.0.11:22 ops@bastion.example.com
```

## ssh - Forward a Local Port

`-L` opens a listener on the workstation and tunnels connections to a host and port reachable from the server. Use it to reach an admin interface that is bound to localhost or to a private network.

```
ssh -L 8080:127.0.0.1:80 ops@server1.example.com
```

The forward target is resolved from the server's point of view, so this reaches a database that only the server can see:

```
ssh -L 5432:db.internal:5432 ops@bastion.example.com
```

Add `-N` to set up the tunnel without running a remote command, and `-f` to background the client once authentication succeeds. Combine with `ExitOnForwardFailure` so a port that is already in use fails loudly instead of leaving a useless background connection.

```
ssh -f -N -o ExitOnForwardFailure=yes -L 5432:db.internal:5432 ops@bastion.example.com
```

By default the listener is bound to loopback. Bind it to a specific local address only when other machines are genuinely meant to use the tunnel.

```
ssh -N -L 192.168.1.10:8080:127.0.0.1:80 ops@server1.example.com
```

## ssh - Forward a Remote Port

`-R` is the reverse: it opens a listener on the server and forwards connections back to the client side. Use it to expose a local service to a machine that cannot dial back to you through a firewall or NAT.

```
ssh -R 9000:127.0.0.1:3000 ops@server1.example.com
```

The remote listener binds to loopback on the server unless sshd is configured with `GatewayPorts yes`, so check that before assuming other hosts can reach it:

```
ssh -R 0.0.0.0:9000:127.0.0.1:3000 ops@server1.example.com
```

For a long-lived reverse tunnel, disable the remote command and fail fast if the port cannot be bound. Note that sshd will not release a stale listener until its old connection times out, which is the usual reason a reconnect silently binds nothing.

```
ssh -N -o ExitOnForwardFailure=yes -R 9000:127.0.0.1:3000 ops@server1.example.com
```

## ssh - Open a SOCKS Proxy

`-D` turns the connection into a SOCKS4/5 proxy, so any application configured to use it routes traffic out through the server. This is the general-purpose alternative to enumerating individual `-L` forwards.

```
ssh -D 1080 ops@bastion.example.com
```

Run it as a background tunnel with no remote session:

```
ssh -f -N -D 1080 ops@bastion.example.com
```

Point a client at it, for example to reach an internal-only endpoint:

```
curl --socks5-hostname 127.0.0.1:1080 http://intranet.internal/health
```

## ssh - Use the Authentication Agent

ssh-agent holds decrypted private keys in memory so a passphrase is typed once per session rather than per connection. Start one and export its socket into the shell.

```
eval "$(ssh-agent -s)"
```

Add a key to the running agent:

```
ssh-add ~/.ssh/id_ed25519
```

Set a lifetime so the key is dropped automatically. On a shared or long-running workstation this limits how long a stolen agent socket is useful.

```
ssh-add -t 8h ~/.ssh/id_ed25519_prod
```

List the fingerprints currently loaded, which is the first thing to check when a key-based login unexpectedly asks for a password:

```
ssh-add -l
```

Print the full public keys the agent is offering:

```
ssh-add -L
```

Remove one key, or flush everything:

```
ssh-add -d ~/.ssh/id_ed25519_prod
```

```
ssh-add -D
```

Have ssh load a key into the agent automatically the first time it is used, instead of remembering to run ssh-add:

```
Host *
    AddKeysToAgent yes
```

## ssh - Forward the Agent to a Remote Host

`-A` makes the local agent reachable from the remote session, so you can hop onward without copying a private key to the intermediate machine.

```
ssh -A ops@bastion.example.com
```

This is genuinely risky: anyone who can reach the agent socket on that host — root, or any process able to bypass file permissions — can use your loaded keys for as long as you are connected. They cannot extract the key material, but they can authenticate as you. Prefer `ProxyJump`, which never exposes the agent to the intermediate host at all.

```
ssh -J ops@bastion.example.com deploy@10.20.0.11
```

If forwarding is unavoidable, scope it to one host in the config rather than enabling it globally, and constrain the key to the destinations it may be used for:

```
Host bastion
    ForwardAgent yes
```

```
ssh-add -h 'bastion.example.com>deploy@10.20.0.11' ~/.ssh/id_ed25519_deploy
```

## ssh - Reuse Connections with Multiplexing

A master connection can carry additional sessions, so subsequent commands to the same host skip the TCP handshake and key exchange entirely. On a config-management run that opens dozens of connections this is the single largest speed-up available.

```
Host *
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
```

`ControlPersist` keeps the master alive in the background after the last session closes, so the next command reuses it. Set up the same thing ad hoc:

```
ssh -M -S ~/.ssh/cm-web1 -o ControlPersist=10m -N -f ops@server1.example.com
```

Ask whether a master is currently running for a destination:

```
ssh -O check -S ~/.ssh/cm-web1 ops@server1.example.com
```

Tear the master down, which is what you need when a config change is not taking effect because sessions are still riding an old connection:

```
ssh -O exit -S ~/.ssh/cm-web1 ops@server1.example.com
```

Bypass multiplexing for a single command without editing the config:

```
ssh -S none ops@server1.example.com
```

## ssh - Keep a Session Alive

Idle sessions are commonly killed by stateful firewalls and NAT devices long before sshd times them out. `ServerAliveInterval` makes the client send an encrypted keepalive through the channel, which both holds the mapping open and detects a dead peer.

```
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
```

With those values the client gives up after roughly 90 seconds of silence instead of hanging indefinitely. Apply it to one connection:

```
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=3 ops@server1.example.com
```

Cap how long the initial connection attempt may block, which matters in scripts iterating over hosts that may be down:

```
ssh -o ConnectTimeout=5 ops@server1.example.com uptime
```

## ssh - Manage Known Host Keys

Every accepted host key is recorded in `~/.ssh/known_hosts`. Look up an entry, which works even when the file is hashed:

```
ssh-keygen -F server1.example.com
```

Remove an entry after a server has been genuinely rebuilt. This is the correct response to the "REMOTE HOST IDENTIFICATION HAS CHANGED" warning — never edit the line out blindly, and never disable the check.

```
ssh-keygen -R server1.example.com
```

Fetch a host's public keys so they can be reviewed and added to a known_hosts file up front, rather than trusting whatever answers on first connection:

```
ssh-keyscan -t ed25519 server1.example.com >> ~/.ssh/known_hosts
```

Check the fingerprint of what was fetched against the value the server operator reports:

```
ssh-keyscan -t ed25519 server1.example.com | ssh-keygen -lf -
```

Accept new hosts automatically but still refuse changed keys. This is the right setting for provisioning freshly built machines; plain `no` also accepts changed keys and gives up the protection entirely.

```
ssh -o StrictHostKeyChecking=accept-new ops@server1.example.com
```

Hash existing entries so the file does not disclose which hosts you connect to. Keep the `.old` backup it writes until you have confirmed logins still work.

```
ssh-keygen -H -f ~/.ssh/known_hosts
```

## ssh - Debug a Failed Connection

`-v` prints what the client is doing at each stage. It is by far the most useful troubleshooting flag: it shows which config files were read, which keys were offered and in what order, and where the server rejected the attempt.

```
ssh -v ops@server1.example.com
```

Increase to three levels for full protocol detail, including key exchange and algorithm negotiation:

```
ssh -vvv ops@server1.example.com
```

Send the debug output to a file instead of the terminal, so it can be attached to a ticket without the session output mixed in:

```
ssh -vvv -E /tmp/ssh-debug.log ops@server1.example.com
```

When the client side looks correct, the answer is in the server log. Authentication failures are reported there with the reason, which the client is deliberately not told.

```
ssh ops@server1.example.com 'sudo journalctl -u ssh -n 100 --no-pager'
```

Validate an sshd configuration before restarting the service, so a syntax error does not lock everyone out:

```
ssh ops@server1.example.com 'sudo sshd -t'
```

## ssh - Copy Files with scp

Copy a local file to a remote path. Since OpenSSH 9.0 scp transfers over the SFTP protocol by default, so remote-side shell glob expansion no longer happens the way it used to.

```
scp ./app.conf ops@server1.example.com:/etc/app/app.conf
```

Copy a directory recursively:

```
scp -r ./config ops@server1.example.com:/opt/app/
```

Pull a file back, and preserve modification times and modes:

```
scp -p ops@server1.example.com:/var/log/app.log ./app.log
```

Use a non-default port. scp uses capital `-P`, unlike ssh.

```
scp -P 2222 ./app.conf ops@server1.example.com:/etc/app/
```

Route the transfer through a bastion, using the same jump syntax as ssh:

```
scp -J ops@bastion.example.com ./app.conf deploy@10.20.0.11:/etc/app/
```

Cap bandwidth in Kbit/s so a large copy does not saturate a production link:

```
scp -l 8000 ./backup.tar.gz ops@server1.example.com:/srv/backups/
```

Fall back to the legacy SCP protocol for a server whose SFTP subsystem is disabled or broken:

```
scp -O ./app.conf ops@server1.example.com:/etc/app/
```

## ssh - Transfer Files with sftp

sftp gives an interactive session with directory listing and tab completion, which is easier than scp when you do not already know the remote paths.

```
sftp ops@server1.example.com
```

Open directly in a remote directory:

```
sftp ops@server1.example.com:/srv/backups
```

Run a scripted batch of commands non-interactively, which is how to use sftp from cron or a pipeline:

```
sftp -b ./transfer.txt ops@server1.example.com
```

The batch file holds ordinary sftp commands; prefix a line with `-` to continue past a failure.

```
cd /srv/backups
put ./backup.tar.gz
-rm old-backup.tar.gz
bye
```

Connect through a jump host, or on a non-default port with capital `-P`:

```
sftp -J ops@bastion.example.com -P 2222 deploy@10.20.0.11
```

## ssh - Run Commands Non-Interactively

`BatchMode=yes` disables every interactive prompt, so a missing key fails immediately with an error instead of hanging a script waiting for a passphrase that will never be typed.

```
ssh -o BatchMode=yes ops@server1.example.com 'systemctl is-active nginx'
```

`-n` redirects stdin from /dev/null. Without it, a loop like this one has its input consumed by the first ssh invocation and processes only one host.

```
while read -r host; do ssh -n -o BatchMode=yes "ops@$host" 'uptime'; done < hosts.txt
```

`-T` suppresses pty allocation, which keeps the remote output clean of terminal control characters when it is being parsed:

```
ssh -T -n ops@server1.example.com 'df -h --output=pcent,target'
```

Run against many hosts in parallel and tag each line with its source, which is enough for most one-off fleet queries without reaching for a config-management tool:

```
xargs -P 10 -I{} ssh -n -o BatchMode=yes -o ConnectTimeout=5 ops@{} 'uname -r' < hosts.txt
```

Combine quiet mode with a checked exit status for health probes in a pipeline:

```
ssh -q -o BatchMode=yes ops@server1.example.com 'test -f /var/run/app.pid' && echo up
```

## ssh - Restrict What a Key May Do

Options prefixed to a line in the server's `authorized_keys` constrain that specific key. `command=` forces a fixed command regardless of what the client asks for, which turns a general-purpose key into a single-purpose one.

```
command="/usr/local/bin/backup-receive",restrict ssh-ed25519 AAAAC3Nza... backup-job
```

`restrict` disables port, agent and X11 forwarding plus pty allocation, and automatically includes any restriction added in future OpenSSH releases. Re-enable individual capabilities after it when they are genuinely needed:

```
restrict,pty,command="/usr/local/bin/maintenance-menu" ssh-ed25519 AAAAC3Nza... oncall
```

`from=` limits which source addresses may use the key, which is worth adding to any unattended key even when a firewall already restricts access:

```
from="10.20.0.0/24,!10.20.0.99",no-port-forwarding ssh-ed25519 AAAAC3Nza... deploy@ci
```

Limit where a key may open forwards rather than banning forwarding outright:

```
permitopen="10.20.0.11:5432",no-pty ssh-ed25519 AAAAC3Nza... dba-tunnel
```

The command the client originally asked for is still available to a forced command, so a wrapper script can inspect and whitelist it:

```
ssh ops@server1.example.com 'echo "$SSH_ORIGINAL_COMMAND"'
```

## ssh - Fix Permissions on ~/.ssh

Both ends of an SSH connection refuse to use credentials that other users could tamper with. On the client, a private key readable by anyone else is rejected outright with "WARNING: UNPROTECTED PRIVATE KEY FILE!" and "Permissions ... are too open".

```
chmod 700 ~/.ssh
```

```
chmod 600 ~/.ssh/id_ed25519 ~/.ssh/config
```

Public keys and known_hosts may be world-readable, but must not be world-writable:

```
chmod 644 ~/.ssh/id_ed25519.pub ~/.ssh/known_hosts
```

On the server the same applies to `authorized_keys`, and — the part most often missed — to the home directory itself. Under the default `StrictModes yes`, sshd silently ignores `authorized_keys` if the home directory or `~/.ssh` is writable by group or others, and the login falls back to a password prompt with no client-side clue why.

```
ssh ops@server1.example.com 'chmod 755 ~ && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'
```

Check ownership too, since a file copied in as root will not be read for an unprivileged account:

```
ssh ops@server1.example.com 'ls -ld ~ ~/.ssh ~/.ssh/authorized_keys'
```

Confirm the diagnosis in the server log, where StrictModes rejections are recorded as "Authentication refused: bad ownership or modes for directory":

```
ssh ops@server1.example.com 'sudo journalctl -u ssh -n 50 --no-pager | grep -i refused'
```
