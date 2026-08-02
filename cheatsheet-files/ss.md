# ss

ss dumps socket statistics from the kernel, showing listening ports, established connections, and their owning processes. It reads the netlink socket-diag interface rather than parsing /proc, which makes it fast enough to use on servers holding tens of thousands of connections.

#platform/multiple #target/Linux #cat/Networking

% ss, sockets, networking, tcp, udp, ports, netstat, connections, listening

## ss - List Listening Sockets

Listening sockets are hidden by default, so `-l` is what answers "what is bound on this box".

```
ss -l
```

Restrict to listening TCP sockets, which is the usual question:

```
ss -lt
```

Restrict to bound UDP sockets:

```
ss -lu
```

## ss - Select TCP or UDP Sockets

With no family flag ss dumps every family it can reach, including unix and netlink, which is rarely what you want. Narrow it to TCP.

```
ss -t
```

Narrow it to UDP:

```
ss -u
```

Show both listening and non-listening sockets. Without `-a` you see only connected sockets, so a port you know is open appears to be missing:

```
ss -ta
```

Ask for several socket tables explicitly:

```
ss -A tcp,udp
```

Select by address family instead of protocol:

```
ss -f inet
```

## ss - Skip Name Resolution

`-n` stops ss resolving port numbers to service names, so `443` stays `443` instead of becoming `https`. Beyond readability this avoids a lookup per socket, which is the difference between instant and multi-second output on a busy host.

```
ss -tn
```

Combined with `-a` for a full numeric TCP picture:

```
ss -tan
```

## ss - Show the Owning Process

`-p` appends the process name, PID, and file descriptor holding each socket, which is how you go from "port 8080 is taken" to "kill that process".

```
ss -tlp
```

Sockets owned by other users show no process unless ss runs as root. The rows are still listed, just with an empty Process column, which is easy to misread as "no owner":

```
sudo ss -tlp
```

Show the specific thread rather than just the process. This implies `-p`:

```
ss -tlT
```

## ss - Audit Every Listening Port

`-tulpn` is the single most used invocation: TCP and UDP, listening only, numeric, with process names. It is the standard first command when auditing what a server exposes.

```
ss -tulpn
```

Run it as root so listeners owned by system daemons show their process names:

```
sudo ss -tulpn
```

Check whether one specific port is bound before starting a service:

```
ss -tulpn | grep ':8080 '
```

## ss - Print Summary Statistics

`-s` prints counts per protocol and per TCP state without enumerating sockets. It pulls from summary counters instead of walking the socket tables, so it stays fast when a host has so many sockets that a full dump is painful.

```
ss -s
```

A rising `timewait` or `closed` count here is the quickest signal of a connection churn problem.

## ss - Show Extended Socket Information

`-e` adds the owning UID, the socket inode, and the socket cookie. The UID identifies the owner even when you cannot see the process name, and the inode ties a socket back to an entry under /proc/<pid>/fd.

```
ss -tne
```

## ss - Show Socket Memory Usage

`-m` prints the per-socket memory breakdown as `skmem:(r<rmem_alloc>,rb<rcv_buf>,t<wmem_alloc>,tb<snd_buf>,...)`. Use it when a process is accumulating memory in kernel socket buffers rather than in its own heap.

```
ss -tnm
```

Look at the buffers of listening sockets, where a large `r` value means the application is not accepting fast enough:

```
ss -tlnm
```

## ss - Show Internal TCP Information

`-i` exposes the kernel's per-connection TCP state: congestion algorithm, `cwnd`, `rtt`/`rttvar`, `retrans`, `mss`, and byte and segment counters. This is the data you need to tell a slow application apart from a lossy network.

```
ss -tni
```

Inspect the congestion window and round-trip time for connections to one host:

```
ss -tni state established 'dst <ip>'
```

A non-zero `retrans` field and a `cwnd` stuck at a low value point at packet loss on the path, not at the application.

## ss - Show Timer Information

`-o` prints the active kernel timer per socket as `timer:(<name>,<expire>,<retrans>)`. The `retrans` counter is a live retransmission count, and a `persist` timer means the peer has advertised a zero window.

```
ss -tno
```

Look at the timers on sockets stuck half-closed, which is how you find a peer that stopped acknowledging:

```
ss -tno state fin-wait-1
```

## ss - Inspect Unix Domain Sockets

`-x` selects unix domain sockets, used by everything local: Docker, systemd, databases, PHP-FPM.

```
ss -x
```

List only the unix sockets being listened on, with the paths they are bound to:

```
ss -xl
```

Match a socket path with a glob. Unix addresses are matched as fnmatch patterns, not as regexes:

```
ss -xl 'src /run/*'
```

## ss - Restrict to IPv4 or IPv6

`-4` shows only IPv4 sockets. Use it when a dual-stack listener makes the output twice as long as it needs to be.

```
ss -4 -tuln
```

Show only IPv6 sockets, which is how to confirm a service really is bound on v6 and not just on v4:

```
ss -6 -tuln
```

## ss - Resolve Names and Ports

`-r` resolves numeric addresses back to hostnames. It is the opposite of `-n` and costs a DNS lookup per socket, so it is for reading a short list, never for a busy server.

```
ss -tr state established
```

## ss - Filter by Socket State

A `state` filter goes before any address expression and takes any standard TCP state name.

```
ss -tn state established
```

List sockets that are listening. This is equivalent to `-l` but composes with the rest of the filter language:

```
ss -tn state listening
```

Find sockets sitting in TIME-WAIT, which accumulate when a host closes many short-lived connections:

```
ss -tn state time-wait
```

Other useful states are `syn-sent` (a connection that is not being answered), `close-wait` (the application has not closed its side), and `fin-wait-1`:

```
ss -tn state close-wait
```

Invert a state selection with `exclude`:

```
ss -tn exclude established
```

## ss - Use State Groups

Instead of listing states one by one, ss defines groups. `connected` is every state except listening and closed.

```
ss -tn state connected
```

`synchronized` is every connected state except syn-sent, so it covers connections that actually completed a handshake:

```
ss -tn state synchronized
```

`bucket` is the minisocket states, time-wait and syn-recv, and `big` is everything else:

```
ss -tn state bucket
```

`all` includes every state, which is what `-a` sets implicitly:

```
ss -tn state all
```

## ss - Filter by Port

`sport` and `dport` compare against a port, which is written with a leading colon. Without the colon the value is parsed as an address.

```
ss -tn 'dport = :443'
```

Match on the local port instead:

```
ss -tuln 'sport = :53'
```

Ports also accept service names from /etc/services:

```
ss -tn 'dport = :https'
```

Comparison operators `<`, `<=`, `=`, `!=`, `>=`, `>` all work, so a port range is two predicates:

```
ss -tanp 'sport >= :8000 and sport <= :9000'
```

Match a port on either side of the connection. The parentheses are separate shell words, so keep the spaces inside them:

```
ss -tan '( sport = :22 or dport = :22 )'
```

## ss - Filter by Address

`dst` and `src` match the peer and local addresses. A bare address matches any port on that host.

```
ss -tn 'dst <ip>'
```

Pin the port as well by appending it to the address:

```
ss -tn 'dst <ip>:443'
```

An address may carry a CIDR prefix, which is how you select a whole network:

```
ss -tan 'dst 10.0.0.0/8'
```

Find loopback-only traffic:

```
ss -tn 'src 127.0.0.0/8'
```

Filter on the interface a connection uses. The name is resolved to an interface index when the filter is parsed, so a device that does not exist is rejected with `Cannot parse device` rather than returning nothing:

```
ss -tan 'dev = <interface>'
```

## ss - Combine and Negate Filters

Predicates combine with `and`, `or`, and `not`, in increasing order of precedence, and group with parentheses. Adjacent predicates with no operator are an implicit `and`.

```
ss -tan '( dport = :80 or dport = :443 ) and dst 10.0.0.0/8'
```

A state filter can be combined with an expression, which is the usual shape of a real debugging command:

```
ss -tan state time-wait 'dport = :443'
```

Negate a whole predicate with `not`:

```
ss -tn 'not dst 127.0.0.0/8'
```

Note the asymmetry: ports accept `!=` directly, but `dst`/`src` do not. `dst != <ip>` is a parse error, so addresses must be negated with `not`:

```
ss -tan 'dport != :443'
```

## ss - Filter by Process or Cgroup

There is no PID predicate in the filter language, so process-based selection means filtering the `-p` output:

```
ss -tanp | grep '"nginx"'
```

Sockets can be selected by the cgroup that owns them, which on a systemd host means selecting by service. The path is relative to the cgroup v2 mount point and must be given in full. ss resolves it to a cgroup ID while parsing the filter, so a path that does not exist fails with `Cannot parse cgroup` instead of matching nothing:

```
ss -tan 'cgroup = /system.slice/<unit>.service'
```

Show which cgroup each socket belongs to, to find the path to match on:

```
ss -tn --cgroup
```

Match sockets whose source port was assigned by the kernel rather than bound explicitly:

```
ss -tan 'autobound'
```

## ss - Count Connections

Tally sockets per TCP state to see at a glance whether a host is leaking TIME-WAIT or CLOSE-WAIT sockets.

```
ss -tan | awk 'NR>1 {print $1}' | sort | uniq -c | sort -rn
```

Count established connections per remote address, which finds the client hammering a service. `-H` drops the header so awk does not have to skip it, and selecting a single state drops the State column, which is why the peer address is field 4:

```
ss -tnH state established | awk '{print $4}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -20
```

Count connections to one listening port, for comparing against a connection limit:

```
ss -tnH state established 'sport = :443' | wc -l
```

## ss - Produce Script-Friendly Output

`-H` suppresses the header line so the output can be piped straight into awk or a monitoring check.

```
ss -tnH state established
```

`-O` keeps each socket on a single line. The extra output from `-i` and `-m` normally wraps onto a continuation line, which breaks line-oriented parsing:

```
ss -tniO
```

## ss - Forcibly Close a Socket

`-K` destroys the matching sockets in the kernel instead of listing them. It is destructive: the application sees the connection drop with no clean shutdown. It requires root and a kernel built with CONFIG_INET_DIAG_DESTROY, supports IPv4 and IPv6 only, and silently skips sockets the kernel cannot close.

```
sudo ss -K 'dst <ip>'
```

Always run the same filter without `-K` first to see exactly what it selects. Use it to clear connections from a specific peer:

```
sudo ss -K 'dst <ip>:443'
```

## ss - Replace netstat

ss is the iproute2 replacement for the deprecated net-tools netstat. netstat reads and re-parses /proc/net/tcp for every socket, which degrades badly past a few thousand connections, while ss queries the kernel over netlink and can push filtering into the kernel instead of dumping everything and discarding rows in userspace.

```
ss -tulpn
```

The netstat command it replaces, for anyone migrating muscle memory:

```
netstat -tulpn
```

The other common translations are `netstat -an` to `ss -an`, `netstat -s` to `ss -s`, and `netstat -x` to `ss -x`. The state and address filters have no netstat equivalent at all, which is the main reason to switch.
