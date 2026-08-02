# systemctl

systemctl is the control and inspection client for the systemd service manager. It starts, stops, enables and inspects units — services, sockets, timers, mounts and targets — and is the primary tool for running and debugging daemons on an on-premise Linux host.

#platform/multiple #target/Linux #cat/SystemAdministration

% systemctl, systemd, services, units, daemons, boot, timers, cgroups

## systemctl - Check the systemd Version and Global State

Print the systemd version and the compile-time feature flags. Worth checking first, because verbs and options differ noticeably between major versions.

```
systemctl --version
```

Report whether the machine came up cleanly. It prints `running`, or `degraded` when at least one unit failed, and exits non-zero in that case — which makes it a cheap post-boot health gate.

```
systemctl is-system-running
```

Block until boot has finished before continuing, useful at the top of a provisioning script:

```
systemctl is-system-running --wait
```

## systemctl - Start Stop and Restart a Service

Start a unit now. This has no effect on whether it comes back after a reboot.

```
sudo systemctl start nginx.service
```

Stop it:

```
sudo systemctl stop nginx.service
```

Restart it, which starts the unit even if it was not running:

```
sudo systemctl restart nginx.service
```

Restart only if the unit is currently active. Use this in package post-install scripts so you do not accidentally start a service the operator had deliberately stopped:

```
sudo systemctl try-restart nginx.service
```

Block until the unit has finished starting instead of returning as soon as the job is queued:

```
sudo systemctl start --wait backup.service
```

## systemctl - Reload Instead of Restarting

Ask the daemon to re-read its configuration without dropping connections. This only works if the unit defines `ExecReload=`; a restart kills the process, a reload does not.

```
sudo systemctl reload nginx.service
```

Reload if the unit supports it, otherwise fall back to a restart. This is the safe form for a config-management run, where you do not know in advance whether the unit has an `ExecReload=`.

```
sudo systemctl reload-or-restart nginx.service
```

The same, but leave the unit alone when it is not currently active:

```
sudo systemctl try-reload-or-restart nginx.service
```

## systemctl - Show Service Status

Print the runtime state of a unit: whether it is loaded and enabled, the main PID, memory and CPU accounting, its cgroup, and the last log lines. This is the first command to run when a service misbehaves.

```
systemctl status nginx.service
```

Widen the log tail, and disable the pager so the output is usable in a pipeline:

```
systemctl status nginx.service -n 50 --no-pager
```

Find out which unit a stray process belongs to by passing its PID:

```
systemctl status 1823
```

Follow the unit's logs afterwards, since `status` only shows a short tail:

```
journalctl -u nginx.service -f
```

## systemctl - Query Unit State in Scripts

Check whether a unit is running. It prints the state and exits 0 only when active — 3 for a failed or inactive unit, 4 when the unit does not exist at all.

```
systemctl is-active nginx.service
```

Check whether it is wired up to start at boot. Exit code 0 means enabled; the printed word distinguishes `enabled`, `static`, `masked` and `disabled`.

```
systemctl is-enabled nginx.service
```

Check specifically for the failed state. This exits 0 when the unit *is* failed, the inverse convention of `is-active`, so do not mix them up in an `if`.

```
systemctl is-failed nginx.service
```

Suppress the printed word and rely on the exit code alone, which is what you want inside a health check:

```
systemctl is-active --quiet nginx.service && echo up
```

## systemctl - Enable a Service at Boot

Create the symlinks that make a unit start at boot. `enable` alone does not touch the running system — the service will not be running until the next boot.

```
sudo systemctl enable nginx.service
```

Enable and start in one step, which is almost always what you actually meant:

```
sudo systemctl enable --now nginx.service
```

Recreate the symlinks from scratch after changing the `[Install]` section, since a plain `enable` will not remove stale links:

```
sudo systemctl reenable nginx.service
```

Enable only until the next reboot by writing the links under `/run` instead of `/etc`:

```
sudo systemctl enable --runtime --now nginx.service
```

## systemctl - Disable Mask and Unmask a Unit

Remove the boot-time symlinks. The unit can still be started manually, and can still be pulled in as a dependency of something else.

```
sudo systemctl disable --now nginx.service
```

Mask a unit to make it unstartable. This links the unit name to `/dev/null`, so manual starts, socket activation and dependency activation all fail — this is the only reliable way to keep a vendor unit down.

```
sudo systemctl mask nginx.service
```

Remove the mask:

```
sudo systemctl unmask nginx.service
```

Mask only until the next reboot, which is useful during a maintenance window:

```
sudo systemctl mask --runtime --now nginx.service
```

Throw away every local override and drop-in and go back to the vendor unit file shipped in `/usr/lib/systemd/system`:

```
sudo systemctl revert nginx.service
```

## systemctl - List Units Currently in Memory

List the units systemd has loaded, with their load, active and sub states.

```
systemctl list-units
```

Restrict to services, which is the usual starting point on a server:

```
systemctl list-units --type=service
```

Filter by state rather than by type — `--state` matches LOAD, ACTIVE or SUB values:

```
systemctl list-units --type=service --state=running
```

Include units that are loaded but dead, which `list-units` hides by default:

```
systemctl list-units --type=service --all
```

Match by glob and strip the headers and pager so the output can be parsed:

```
systemctl list-units 'docker*' --no-legend --no-pager
```

## systemctl - List Installed Unit Files

List every unit file on disk with its enablement state. Unlike `list-units`, this shows units that have never been loaded.

```
systemctl list-unit-files
```

Show only what is set to start at boot, which is the fastest way to audit a host's autostart surface:

```
systemctl list-unit-files --type=service --state=enabled
```

Find everything that has been masked:

```
systemctl list-unit-files --state=masked
```

Compare against the distribution preset, whose column tells you what the vendor intended:

```
systemctl list-unit-files --type=service --no-pager
```

## systemctl - Find and Clear Failed Units

List every unit in the failed state. Run this after a boot or a deploy before declaring success.

```
systemctl --failed
```

The same thing spelled out, which also accepts other states:

```
systemctl list-units --state=failed
```

Clear the failed flag and reset the restart-rate counter. A unit that hit `StartLimitBurst=` will refuse to start again until this is done, so this is the fix for "Start request repeated too quickly".

```
sudo systemctl reset-failed nginx.service
```

Reset every failed unit at once:

```
sudo systemctl reset-failed
```

## systemctl - Read the Effective Unit Definition

Print the unit file together with every drop-in that applies to it, each preceded by a comment giving its path. Always read this rather than the vendor file, because drop-ins may be changing the behaviour you are looking at.

```
systemctl cat nginx.service
```

Show a timer and the service it activates in one go:

```
systemctl cat logrotate.timer logrotate.service
```

Open the unit's own manual page, as declared by its `Documentation=` line:

```
systemctl help cron.service
```

## systemctl - Override a Unit with a Drop-In

Open an override file for the unit. This writes `/etc/systemd/system/<unit>.d/override.conf`, leaving the vendor unit in `/usr/lib/systemd/system` untouched so package upgrades do not clobber your change — and it runs a daemon-reload for you on save.

```
sudo systemctl edit nginx.service
```

Give the drop-in a meaningful file name instead of `override.conf`, which matters when several roles each add a fragment:

```
sudo systemctl edit --drop-in=limits.conf nginx.service
```

Copy the whole unit into `/etc/systemd/system` and edit that instead. Use this only when a drop-in cannot express the change — for example to remove an `ExecStart=` line, since drop-ins can only append unless you first reset the directive with an empty assignment.

```
sudo systemctl edit --full nginx.service
```

Create a brand-new unit file from scratch:

```
sudo systemctl edit --force --full myapp.service
```

Check the result parses before you rely on it:

```
systemd-analyze verify /etc/systemd/system/myapp.service
```

## systemctl - Reload the Manager After Editing Units

Tell systemd to re-read unit files from disk. This is required after hand-editing anything under `/etc/systemd/system` or `/usr/lib/systemd/system`; `systemctl edit` does it automatically, a text editor does not. It regenerates units and re-runs generators, but does not restart anything.

```
sudo systemctl daemon-reload
```

Re-execute the systemd binary itself, which is what you need after upgrading the systemd package so PID 1 picks up the new code:

```
sudo systemctl daemon-reexec
```

## systemctl - Show Unit Properties

Dump every property of a unit as `Key=Value` pairs. This is the machine-readable counterpart to `status`, and exposes fields `status` never prints.

```
systemctl show nginx.service
```

Select individual properties, which is how you script against systemd without parsing prose:

```
systemctl show cron.service -p ExecStart -p Restart -p FragmentPath
```

Print just the value, with no `Key=` prefix, so it can be assigned to a shell variable:

```
systemctl show -P MainPID cron.service
```

Query the manager itself rather than a unit:

```
systemctl show -p Version -p Architecture
```

Include properties that are currently unset, which are omitted by default:

```
systemctl show nginx.service --all
```

## systemctl - Inspect Dependencies

Show, as a tree, the units this one pulls in. The bullet colour reflects each dependency's current state, so a broken requirement is visible immediately.

```
systemctl list-dependencies nginx.service
```

Invert the question and show what depends on this unit — run this before stopping anything on a production box.

```
systemctl list-dependencies nginx.service --reverse
```

Show ordering rather than requirement dependencies, that is, what must start before or after this unit:

```
systemctl list-dependencies nginx.service --after
```

Flatten the tree into a plain list for grepping:

```
systemctl list-dependencies multi-user.target --plain --no-pager
```

## systemctl - Work with Targets

Print the target the machine boots into.

```
systemctl get-default
```

Switch a server to text mode so it stops starting a display manager at boot:

```
sudo systemctl set-default multi-user.target
```

Switch to a target immediately, stopping everything not required by it. This is disruptive — it will tear down active services — so prefer it on a console, not over the SSH session you are relying on.

```
sudo systemctl isolate multi-user.target
```

Drop to single-user rescue mode for filesystem work:

```
sudo systemctl rescue
```

List the targets the system knows about:

```
systemctl list-units --type=target --all
```

## systemctl - Manage Timers

List every timer with its next and last elapse time. Timers replace cron entries and are worth preferring on systemd hosts because the triggered job is a real unit: it gets its own logs, its own cgroup, resource limits, and a failure state you can alert on.

```
systemctl list-timers
```

Include timers that are not currently active:

```
systemctl list-timers --all --no-pager
```

Read a timer and the service it activates, to see the `OnCalendar=` schedule and the command behind it:

```
systemctl cat logrotate.timer logrotate.service
```

Run the triggered job once by hand, without waiting for the schedule, which is how you test it:

```
sudo systemctl start logrotate.service
```

Check a calendar expression before putting it in a unit:

```
systemd-analyze calendar 'Mon *-*-* 03:30:00'
```

## systemctl - Analyze Boot Performance

Print how long firmware, bootloader, kernel and userspace each took.

```
systemd-analyze time
```

List units by how long they took to initialise. The slowest unit is not necessarily the problem — a slow unit that nothing waits on costs you nothing.

```
systemd-analyze blame
```

Show the chain of units that actually delayed reaching the default target. This is the list to fix, because these are on the critical path.

```
systemd-analyze critical-chain
```

Trace the chain leading to one specific unit:

```
systemd-analyze critical-chain nginx.service
```

Render the whole boot as an SVG timeline for a report:

```
systemd-analyze plot > boot.svg
```

## systemctl - Inspect Resource Usage and Cgroups

Every service runs in its own cgroup, and `status` prints it along with current memory, CPU time and task count — which is how you attribute usage to a service rather than to a stray PID.

```
systemctl status nginx.service
```

Read the accounting counters directly, for feeding into monitoring:

```
systemctl show nginx.service -p ControlGroup -p MemoryCurrent -p TasksCurrent -p CPUUsageNSec
```

Show live resource usage per cgroup, ordered like `top`. Use this to find which service is eating the box.

```
systemd-cgtop
```

Take a single non-interactive sample for a script or a ticket:

```
systemd-cgtop -n 1 -b --depth=2
```

Show the process tree grouped by unit:

```
systemd-cgls -u nginx.service
```

## systemctl - Set Resource Limits at Runtime

Apply a cgroup property to a running unit without editing its file. Without `--runtime` the change is also written to a drop-in and survives reboots.

```
sudo systemctl set-property nginx.service MemoryMax=512M
```

Apply it only until the next reboot, which is the right choice when firefighting:

```
sudo systemctl set-property --runtime nginx.service CPUQuota=50%
```

Confirm it took effect:

```
systemctl show nginx.service -p MemoryMax -p CPUQuota
```

## systemctl - Signal Freeze and Clean a Unit

Send a signal to a unit's processes without going through stop, for example to trigger a config reload or a stack dump the unit has no `ExecReload=` for.

```
sudo systemctl kill -s SIGHUP nginx.service
```

Target only the main process rather than every process in the cgroup:

```
sudo systemctl kill --kill-whom=main -s SIGTERM nginx.service
```

Suspend a unit's processes without killing them, which lets you inspect a misbehaving service while it holds still, then resume it:

```
sudo systemctl freeze nginx.service
sudo systemctl thaw nginx.service
```

Delete a stopped unit's cache, runtime and state directories — the ones declared by `CacheDirectory=`, `RuntimeDirectory=` and friends:

```
sudo systemctl clean --what=cache,runtime nginx.service
```

## systemctl - Manage User Services

Talk to the calling user's own service manager instead of the system one. User units live in `~/.config/systemd/user` and need no root, which suits agents and per-user tooling.

```
systemctl --user list-units --type=service
```

Enable a user unit at login:

```
systemctl --user enable --now myagent.service
```

Reload the user manager after editing a user unit:

```
systemctl --user daemon-reload
```

Install a user unit for every future login on the machine:

```
sudo systemctl --global enable myagent.service
```

User units normally stop when the last session ends, so allow the user's manager to keep running at boot:

```
sudo loginctl enable-linger deploy
```

## systemctl - Operate on a Remote Host or Alternate Root

Run against another machine over SSH. Handy for a quick check across a fleet without opening an interactive session.

```
systemctl -H deploy@server1.example.com status nginx.service
```

Target a local container or VM registered with machined:

```
systemctl -M web-container list-units --type=service
```

Operate on unit files inside a mounted root filesystem — a chroot, a rescue mount, or an image being built. With `--root` systemctl edits the files directly instead of talking to a running manager, so it works when no systemd is running there.

```
sudo systemctl --root=/mnt/target enable nginx.service
```

Do the same against a disk image without mounting it first:

```
sudo systemctl --image=/var/lib/machines/web.raw list-unit-files --type=service
```

## systemctl - Inspect and Change Manager Configuration

Dump the environment block systemd passes to every unit it spawns. Units do not inherit your shell's environment, so this is where to look when a service cannot see a variable.

```
systemctl show-environment
```

Add a variable for units started from now on. It does not affect already-running services, and it is lost on reboot — put anything permanent in the unit or in `/etc/systemd/system.conf`.

```
sudo systemctl set-environment HTTP_PROXY=http://proxy:3128
```

Remove one again:

```
sudo systemctl unset-environment HTTP_PROXY
```

Raise the manager's own log verbosity while debugging a startup problem, then put it back:

```
sudo systemctl log-level debug
sudo systemctl log-level info
```

## systemctl - Power Off and Reboot

Reboot the machine, running the normal shutdown sequence.

```
sudo systemctl reboot
```

Power it off:

```
sudo systemctl poweroff
```

Restart userspace only, leaving the kernel and the hardware initialisation alone. This is far faster than a full reboot and is enough to pick up most package updates.

```
sudo systemctl soft-reboot
```

Schedule the reboot rather than doing it now, so users get a wall warning:

```
sudo systemctl reboot --when=+15min
```

Turn a shutdown verb into a no-op that only reports the action, so a command in a script can be rehearsed safely. It is supported by `halt`, `poweroff`, `reboot`, `kexec`, `soft-reboot`, the sleep verbs, `default`, `rescue`, `emergency` and `exit`, and by nothing else.

```
systemctl --dry-run reboot
```

Cancel a scheduled shutdown:

```
sudo systemctl reboot --when=cancel
```
