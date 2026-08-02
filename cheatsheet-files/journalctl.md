# journalctl

journalctl queries the structured, indexed log store written by systemd-journald. On a systemd host it is the single entry point to service logs, kernel messages, and audit records, replacing the need to guess which file under /var/log a daemon writes to.

#platform/multiple #target/Linux #cat/SystemAdministration

% journalctl, systemd, logs, journald, syslog, kernel, dmesg, troubleshooting

## journalctl - Follow a Unit's Logs

Show the logs of one systemd unit. This is the usual first step after a service fails to start or starts misbehaving.

```
journalctl -u nginx.service
```

Follow the stream live, the journal equivalent of tail -f:

```
journalctl -u nginx.service -f
```

Follow but print only the new lines, without the backlog the follow mode normally shows first:

```
journalctl -u nginx.service -f -n 0
```

The .service suffix can be omitted, and a glob matches several units at once:

```
journalctl -u 'php*-fpm' -f
```

## journalctl - Follow Several Units at Once

Repeat -u to interleave the logs of related units in one time-ordered stream. This is how to watch a request cross a proxy into its backend without opening two terminals.

```
journalctl -u nginx.service -u php8.3-fpm.service -f
```

Add the unit name to each line so the interleaved output stays readable:

```
journalctl -u nginx.service -u postgresql.service -f -o with-unit
```

## journalctl - Filter by Boot

Restrict the output to the current boot. Without this the journal spans every boot it has retained, which makes "did this happen since the reboot?" impossible to answer.

```
journalctl -b
```

Show the previous boot, which is where to look after an unexpected reboot or a hard lockup:

```
journalctl -b -1
```

Combine with a unit to see how a service behaved during the boot before last:

```
journalctl -b -2 -u nginx.service
```

Address a boot by its ID when the relative offsets are ambiguous:

```
journalctl -b 91549d3a33704d9180cf182242503ec2
```

## journalctl - List Recorded Boots

Print every boot still present in the journal with its offset, boot ID, and start and end timestamps. Use it to pick the offset to pass to -b, and to spot boots that ended without a clean shutdown.

```
journalctl --list-boots
```

Emit the same list as JSON for a monitoring script:

```
journalctl --list-boots -o json
```

## journalctl - Filter by Time

Bound the query with absolute timestamps. Anything shorter than a full timestamp is completed from the current date, so a bare time means today.

```
journalctl --since "2026-08-01 09:00:00" --until "2026-08-01 10:30:00"
```

Relative and English forms are accepted, which is faster to type during an incident:

```
journalctl --since "30 min ago"
```

```
journalctl --since -1h --until -10min
```

The keywords yesterday, today, tomorrow and now are also understood:

```
journalctl --since yesterday --until today -u nginx.service
```

Print timestamps in UTC when correlating with logs from hosts in other timezones:

```
journalctl --since -1h --utc
```

## journalctl - Filter by Priority

Show only entries at or above a syslog severity. Passing err drops the informational noise and leaves what actually needs attention.

```
journalctl -p err -b
```

Priorities can be given by name or by number, from 0 (emerg) to 7 (debug):

```
journalctl -p 3 -b
```

Give a range to isolate a band of severities, for example emerg through err:

```
journalctl -p 0..3 -b
```

Filter by syslog facility as well, to separate daemon noise from auth events:

```
journalctl --facility=auth,authpriv --since today
```

## journalctl - Read Kernel Messages

Show the kernel ring buffer as recorded in the journal. Unlike dmesg this keeps timestamps and survives across boots.

```
journalctl -k
```

Read the kernel messages of the previous boot, which is how to recover an OOM kill or a disk error that preceded a crash:

```
journalctl -k -b -1
```

Kernel errors only:

```
journalctl -k -p err -b
```

## journalctl - Limit and Reverse the Output

Show the last N entries instead of the whole journal.

```
journalctl -u nginx.service -n 50
```

Show the newest entries first, which avoids paging to the bottom of a large result:

```
journalctl -p err -n 20 -r
```

Open the pager already scrolled to the end:

```
journalctl -u nginx.service -e
```

A leading plus makes -n count forward from the start of the filtered range rather than backward from the end:

```
journalctl --since -1h -n +20
```

## journalctl - Search Message Text

Match the MESSAGE field against a PERL-compatible regular expression. This is faster than piping the whole journal through grep because the filtering happens inside journalctl.

```
journalctl -u nginx.service -g 'timed out'
```

Matching is case insensitive as long as the pattern is all lowercase; force the behaviour explicitly when the pattern contains uppercase:

```
journalctl -g 'Failed' --case-sensitive=true -b
```

```
journalctl -g 'OOM|segfault' --case-sensitive=false -b
```

## journalctl - Filter by Journal Field

Every entry carries trusted metadata fields prefixed with an underscore, which journald sets itself and a process cannot forge. Matching on them is exact and indexed, so it is cheaper than a text search.

```
journalctl _SYSTEMD_UNIT=sshd.service
```

Follow one specific process by PID, useful when several instances of a daemon are running:

```
journalctl _PID=1234
```

Match on the executable name rather than the unit, which catches processes not started by systemd:

```
journalctl _COMM=sudo
```

Show everything logged by one user account:

```
journalctl _UID=1000
```

Filter by syslog identifier, the tag an application sets for itself:

```
journalctl -t cron --since today
```

## journalctl - Combine Field Matches

Several matches on different fields are ANDed together, so this narrows to informational messages from one unit.

```
journalctl _SYSTEMD_UNIT=nginx.service PRIORITY=6
```

Repeating the same field ORs the values:

```
journalctl _COMM=sudo _COMM=su --since today
```

A bare plus sign ORs whole groups of matches, which is how to express "either of these two combinations":

```
journalctl _SYSTEMD_UNIT=nginx.service PRIORITY=3 + _SYSTEMD_UNIT=postgresql.service PRIORITY=3
```

## journalctl - Discover Available Fields

List every field name present in the journal. Use it before writing a field filter, since the set depends on what the running daemons emit.

```
journalctl -N
```

List the values a given field actually takes, which turns guessing at unit or process names into a lookup:

```
journalctl -F _SYSTEMD_UNIT
```

```
journalctl -F PRIORITY
```

## journalctl - Change the Output Format

Print an unambiguous ISO 8601 timestamp with the timezone offset. Prefer this over the default format whenever the output leaves the machine.

```
journalctl -u nginx.service -o short-iso
```

Show all fields of each entry, which is how to see the metadata available for filtering:

```
journalctl -n 1 -o verbose
```

Emit one JSON object per line for ingestion by a log shipper or jq:

```
journalctl -u nginx.service --since -1h -o json
```

Print only the message text, with no timestamp or hostname, when the line will be parsed by something else:

```
journalctl -u nginx.service -o cat
```

Other useful modes are short-precise for microsecond timestamps, short-monotonic for time since boot when analysing boot performance, and json-pretty for reading a single entry by eye:

```
journalctl -b -o short-monotonic -u systemd-udevd.service
```

## journalctl - Select Which Fields Are Printed

Restrict verbose, export and JSON output to the fields that matter, which keeps a shipped log line small. A handful of address fields are always included regardless.

```
journalctl -u nginx.service -o json --output-fields=MESSAGE,PRIORITY,_PID
```

## journalctl - Show Message Explanations

Append the catalog entry for messages that ship one. systemd's own messages carry an explanation of the cause and the usual remedy, which saves a search engine round trip.

```
journalctl -b -p err -x
```

```
journalctl -u nginx.service -xe
```

## journalctl - Read the User Journal

Show the journal of the current user's session manager and its units, rather than the system journal. Anything started by a systemd --user instance logs here.

```
journalctl --user -u syncthing.service
```

Restrict the system journal explicitly, which matters when a command might otherwise pick up both:

```
journalctl --system -p err -b
```

Filter by a user unit from a query that is not otherwise scoped:

```
journalctl --user-unit=dbus.service --since today
```

## journalctl - Read a Journal from Elsewhere

Read journal files from a directory instead of the local machine, for example a /var/log/journal copied off a failed host or a mounted disk.

```
journalctl -D /mnt/rescue/var/log/journal
```

Read a single journal file, which is what an archived file extracted from a backup gives you:

```
journalctl --file /mnt/rescue/var/log/journal/<machine-id>/system.journal
```

Treat a mounted filesystem as the root, so journalctl finds the journal at its usual path underneath:

```
journalctl --root=/mnt/rescue -b -1 -p err
```

Interleave every journal available, including archived and other users' files, rather than only the default set:

```
journalctl -m --since -1h
```

Query the journal of a local container or a registered machine:

```
journalctl -M <container-name> -u nginx.service
```

## journalctl - Inspect Disk Usage

Report the total size of all active and archived journal files. Run it first when /var starts filling up.

```
journalctl --disk-usage
```

Show the header of each journal file, including its state, sequence numbers, and the time range it covers:

```
journalctl --header
```

## journalctl - Reclaim Disk Space

Delete the oldest archived journal files until the total drops below a size. Active files are never removed, so the figure reported by --disk-usage will not fall all the way to the target.

```
sudo journalctl --vacuum-size=500M
```

Drop archived files older than a retention window instead:

```
sudo journalctl --vacuum-time=14d
```

Keep only a fixed number of files:

```
sudo journalctl --vacuum-files=10
```

The three limits can be combined, and combined with a rotation so the current file is archived first and therefore becomes eligible:

```
sudo journalctl --rotate --vacuum-time=7d --vacuum-size=1G
```

## journalctl - Configure Retention and Persistence

The journal is only kept across reboots if /var/log/journal exists. On a host where journalctl -b -1 returns nothing, this directory is missing and the journal lives in tmpfs under /run/log/journal.

```
sudo mkdir -p /var/log/journal && sudo systemd-tmpfiles --create --prefix /var/log/journal
```

Flush what is currently in /run into the persistent store without rebooting:

```
sudo journalctl --flush
```

Retention limits belong in journald.conf: Storage=persistent to force on-disk storage, SystemMaxUse= for a hard cap, and MaxRetentionSec= for a time-based one. Review the effective configuration including drop-ins:

```
systemd-analyze cat-config systemd/journald.conf
```

Apply changes by restarting the journal daemon:

```
sudo systemctl restart systemd-journald
```

## journalctl - Verify Journal Integrity

Check every journal file for internal consistency and, if Forward Secure Sealing is configured, for tampering. Worth running after a power loss or an unclean filesystem.

```
journalctl --verify
```

Force the journal to be written to disk before taking a copy, so nothing is left in the write buffers:

```
sudo journalctl --sync
```

## journalctl - Use journalctl in Scripts

Suppress the pager so output goes straight to the pipe. Without it journalctl blocks on less whenever stdout is a terminal.

```
journalctl -u nginx.service -p err --since -1h --no-pager
```

Suppress the privilege and rotation notices that would otherwise pollute parsed output:

```
journalctl -q -u nginx.service -o cat -n 100
```

Print a cursor after the last entry, and resume from it on the next run, so a poller never re-reads or skips an entry:

```
journalctl -u nginx.service --show-cursor -n 1 --no-pager
```

```
journalctl -u nginx.service --cursor-file=/var/tmp/nginx.cursor --no-pager
```
