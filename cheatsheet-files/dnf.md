# dnf

dnf is the package manager for RPM-based distributions: Fedora, RHEL 8+, Rocky Linux, AlmaLinux and CentOS Stream. It resolves dependencies, drives RPM transactions, manages repositories, and keeps a full transaction history that can be undone.

#platform/multiple #target/Fedora #cat/PackageManagement

% dnf, fedora, rhel, rpm, packages, dnf5, rocky, almalinux, centos, yum, repository, package management

## dnf - Understand the DNF4 and DNF5 Split

There are two incompatible generations in the field. Fedora 41 and later ship DNF5, where `/usr/bin/dnf` is a symlink to `/usr/bin/dnf5`. RHEL 8, RHEL 9, Rocky 8/9 and AlmaLinux 8/9 ship DNF4 (the Python implementation). Check which one a host has before writing automation against it.

```
dnf --version
rpm -q dnf dnf5
readlink -f "$(command -v dnf)"
```

The subcommands that changed name or were dropped. Everything else in this sheet works on both unless noted.

```
dnf check-update                          # DNF5: dnf5 check-upgrade
dnf repolist                              # DNF5: dnf5 repo list (repolist kept as an alias)
dnf repoinfo                              # DNF5: dnf5 repo info
dnf updateinfo list                       # DNF5: dnf5 advisory list
dnf mark install <package>                # DNF5: dnf5 mark user <package>
dnf mark remove <package>                 # DNF5: dnf5 mark dependency <package>
dnf --nobest upgrade                      # DNF5: dnf5 upgrade --no-best
dnf --sec-severity=Critical upgrade       # DNF5: dnf5 upgrade --advisory-severities=Critical
dnf config-manager --set-enabled <repo>   # DNF5: dnf5 config-manager setopt <repo>.enabled=1
dnf history                               # DNF5: subcommand is mandatory, e.g. dnf5 history list
dnf group install <group>                 # DNF5: same, but the groupinstall alias is gone
dnf makecache --timer                     # DNF5: --timer dropped, use the dnf5-makecache.timer unit
dnf shell                                 # DNF5: superseded by dnf5 do
```

Behavioural differences that bite in scripts: DNF5 defaults `best=true` (DNF4 defaults it to `false`), so DNF5 fails rather than silently installing an older version; DNF5 splits the old `strict` option into `skip_broken` and `skip_unavailable`; DNF5's `module` command only supports `list`, `info`, `enable`, `disable` and `reset` (no `install`/`remove`), because modularity is deprecated; and DNF5 fails when an argument to `upgrade`, `downgrade`, `distro-sync` or `mark` does not match an installed package, where DNF4 merely warned.

## dnf - Install Packages

Install a package and everything it depends on.

```
dnf install <package>
```

Pin the exact version, install a local RPM so its dependencies are still resolved from the repositories, or install a whole group with the `@` prefix:

```
dnf install <package>-<version>-<release>
dnf install ./<package>.rpm
dnf install @<group>
```

Reinstall a package whose files were damaged, or replace one package with another in a single transaction so the system is never left without the capability:

```
dnf reinstall <package>
dnf swap <old-package> <new-package>
```

## dnf - Remove Packages

Remove a package and anything that depends on it. Read the transaction summary before confirming — dependent packages are removed too, which on a server can be far more than expected.

```
dnf remove <package>
```

Clean up duplicate versions left by an interrupted transaction, or drop the older copies of install-only packages such as kernels:

```
dnf remove --duplicates
dnf remove --oldinstallonly
```

## dnf - Check for Available Updates

Report pending updates without changing anything. It exits 100 when updates exist, 0 when none do, and 1 on error — which is what makes it usable as a monitoring or pipeline check.

```
dnf check-update
```

Restrict the check to security advisories, or show the changelog entries that would be applied:

```
dnf check-update --security
dnf check-update --changelogs
```

On Fedora 41+ the command is renamed, with the same exit codes:

```
dnf5 check-upgrade
```

## dnf - Upgrade the System

Upgrade every installed package to the newest available version, processing obsoletes.

```
dnf upgrade
```

Upgrade a single package, or force a metadata refresh first so a repository that was just published is actually seen:

```
dnf upgrade <package>
dnf upgrade --refresh
```

`upgrade-minimal` moves each package only as far as the *nearest* version carrying a bugfix, enhancement or security fix, rather than to the latest. Use it on production servers where the goal is to fix a specific issue with the smallest possible version jump:

```
dnf upgrade-minimal
```

Realign every package with what the repositories currently offer, including downgrading packages that are newer than the repository. This is the command for repairing a host that drifted after a third-party repository was removed:

```
dnf distro-sync
```

## dnf - Apply Only Security Updates

Restrict a transaction to packages that carry a security advisory. This is the usual patching policy for on-premise servers under a change-control regime.

```
dnf upgrade --security
```

Combine with `upgrade-minimal` for the smallest version bump that still closes the advisory, filter by severity, or target a specific CVE or advisory ID:

```
dnf upgrade-minimal --security
dnf upgrade --sec-severity=Critical
dnf upgrade --cve=CVE-2024-3094
dnf upgrade --advisory=RHSA-2024:1234
```

List the advisories themselves before deciding:

```
dnf updateinfo list --security
dnf updateinfo info <advisory-id>
```

DNF5 renamed this command to `advisory` and the severity option to `--advisory-severities`:

```
dnf5 advisory list
dnf5 upgrade --advisory-severities=Critical
```

## dnf - Search for a Package

Search names and summaries. Multiple keywords are ANDed by default.

```
dnf search <keyword>
```

Match any keyword instead of all of them, and widen the search to descriptions and URLs:

```
dnf search --all <keyword> <keyword>
```

Query the repository metadata directly when a precise, scriptable answer is needed:

```
dnf repoquery '<glob>'
dnf repoquery --installed --whatrequires <capability>
```

## dnf - Find Which Package Provides a File

Resolve a file path, a binary, or an abstract capability back to the package that provides it. This works for packages that are not installed, which is what makes it different from `rpm -qf`.

```
dnf provides /usr/bin/htop
```

Globs are accepted, which is how to find a config file when only its basename is known:

```
dnf provides '*/nginx.conf'
dnf provides 'libcrypto.so.3()(64bit)'
```

For a file that is already on disk, the RPM database answers instantly without touching the network:

```
rpm -qf /etc/nginx/nginx.conf
```

## dnf - List and Inspect Packages

Print the summary, version, size, source repository and description of a package.

```
dnf info <package>
```

Show every available version across all repositories, which is the prerequisite for pinning or downgrading:

```
dnf --showduplicates list <package>
```

List packages by state. The flag form shown here works on both DNF4 and DNF5; DNF4 also accepts the older positional form (`dnf list installed`).

```
dnf list --installed
```

Other selections worth knowing:

```
dnf list --available
dnf list --upgrades
dnf list --extras
dnf list --obsoletes
dnf list --recent
```

`--extras` is the important one for audits: it lists packages installed on the host that no enabled repository provides any more — typically leftovers from a decommissioned third-party repo or a hand-installed RPM.

Filter by glob:

```
dnf list --installed 'kernel*'
```

## dnf - Work with Package Groups

Groups are named bundles of packages defined in the repository comps metadata. List them, including the hidden ones and their machine-readable IDs.

```
dnf group list
dnf group list --hidden --ids
```

Inspect what a group contains before installing it, then install it by name or ID:

```
dnf group info "Development Tools"
dnf group install "Development Tools"
```

Pull in the optional packages as well, or remove the group:

```
dnf group install --with-optional <group>
dnf group remove <group>
```

The `groupinstall`, `grouplist` and `groupinfo` aliases inherited from yum still work on DNF4 but were removed in DNF5; use the two-word `dnf group ...` form everywhere.

## dnf - Manage Modules and Streams on RHEL 8 and 9

Modules let RHEL 8 and 9 ship several major versions of the same component. Only one stream of a module can be enabled at a time. List them and see which stream is active.

```
dnf module list
dnf module list --enabled
dnf module info nodejs:20
```

Enable a stream, then install a profile from it. Enabling alone changes only which packages are visible; it installs nothing:

```
dnf module enable nodejs:20
dnf module install nodejs:20/common
```

Clear the enabled/disabled state so the default stream applies again, or move an installed module to a different stream in one step:

```
dnf module reset nodejs
dnf module switch-to nodejs:20
```

Modularity is deprecated. Fedora dropped it, and DNF5 keeps only `list`, `info`, `enable`, `disable` and `reset` — there is no `dnf5 module install`. Treat these commands as RHEL/Rocky/Alma 8 and 9 only.

## dnf - List and Inspect Repositories

Show the enabled repositories with their package counts.

```
dnf repolist
```

Include the disabled ones, or show only those:

```
dnf repolist --all
dnf repolist --disabled
```

Print the full configuration of a repository — baseurl, mirrorlist, GPG settings, expiry — which is the fastest way to debug a repo that returns 404s:

```
dnf repoinfo <repoid>
```

On Fedora 41+ these are subcommands of `repo` (the old names survive as aliases):

```
dnf5 repo list --all
dnf5 repo info <repoid>
```

## dnf - Enable and Disable Repositories

Persistently enable or disable a repository. On DNF4 this needs the `dnf-plugins-core` package; the change is written back into the `.repo` file.

```
dnf config-manager --set-enabled <repoid>
dnf config-manager --set-disabled <repoid>
```

DNF5 replaced the flags with subcommands (from `dnf5-plugins`), and writes the override to `99-config_manager.repo` rather than editing the original file:

```
dnf5 config-manager setopt <repoid>.enabled=1
dnf5 config-manager setopt <repoid>.enabled=0
```

For a one-off transaction, override the repository set on the command line instead of persisting anything. This is the safer habit in automation:

```
dnf install <package> --enablerepo=epel
dnf upgrade --disablerepo='*-testing'
```

Pin a single install to exactly one repository by disabling everything first:

```
dnf --disablerepo='*' --enablerepo=baseos install <package>
```

## dnf - Add a Repository

Fetch a vendor-supplied `.repo` file and enable it.

```
dnf config-manager --add-repo https://example.com/repo/example.repo
```

DNF5 splits the two cases — importing a repo file, and defining a repository from a bare baseurl:

```
dnf5 config-manager addrepo --from-repofile=https://example.com/repo/example.repo
dnf5 config-manager addrepo --id=example --set=baseurl=https://example.com/repo/
```

Writing the file by hand under `/etc/yum.repos.d/` is often preferable, because it is the version that belongs in configuration management. `$releasever` and `$basearch` are expanded by dnf at runtime:

```
[example]
name=Example repository
baseurl=https://example.com/repo/$releasever/$basearch/
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://example.com/RPM-GPG-KEY-example
skip_if_unavailable=0
```

Leave `skip_if_unavailable=0` on repositories that matter: with it enabled, dnf silently disables an unreachable repo and reports success, which turns a network outage into a half-patched fleet.

## dnf - Handle GPG Keys for Third-Party Repositories

Import a vendor signing key into the RPM keyring before the first install from their repository. Do this explicitly rather than answering the interactive prompt, so unattended runs behave the same as interactive ones.

```
rpm --import https://example.com/RPM-GPG-KEY-example
```

List the keys currently trusted by RPM, and identify one before removing it:

```
rpm -q gpg-pubkey --qf '%{name}-%{version}-%{release} %{summary}\n'
rpm -e gpg-pubkey-<keyid>-<release>
```

Verify a downloaded RPM against the imported keys before installing it:

```
rpm --checksig <package>.rpm
```

`gpgcheck=1` verifies package signatures, `repo_gpgcheck=1` verifies the repository metadata signature, and `localpkg_gpgcheck=1` extends checking to RPM files installed from disk. Skipping verification should be a deliberate, scoped exception:

```
dnf install --nogpgcheck ./<package>.rpm
```

## dnf - Review the Transaction History

Every transaction is recorded in a database, which makes dnf auditable in a way that plain `rpm` is not. List them newest first.

```
dnf history list
```

Show the transactions that touched a given package — often the fastest answer to "when did this version land, and who did it":

```
dnf history list <package>
```

Show exactly what a transaction did: every package, the command line used, the user, and the release version at the time:

```
dnf history info <transaction-id>
dnf history info last
dnf history info 12..15
```

List the packages a user asked for explicitly, as opposed to those pulled in as dependencies:

```
dnf history userinstalled
```

On DNF5 the subcommand is mandatory, and package filtering moved to an option:

```
dnf5 history list --contains-pkgs=<package>
```

## dnf - Undo and Roll Back a Transaction

Reverse a single transaction: what it installed is removed, what it removed is reinstalled, what it upgraded is downgraded. This is the recovery path after a bad update.

```
dnf history undo <transaction-id>
dnf history undo last
```

Undo *everything* that happened after a given transaction, returning the package set to its state at that point:

```
dnf history rollback <transaction-id>
```

Repeat a transaction, for example to apply the same change on a second host:

```
dnf history redo <transaction-id>
```

Export a transaction and replay it elsewhere, which is the supported way to clone a package set between machines:

```
dnf history store <transaction-id> --output=/var/tmp/txn.json
dnf history replay /var/tmp/txn.json
```

Undo and rollback only work if the older packages are still obtainable from a repository or the local cache; on a host that runs `dnf clean packages` against a repository that only carries the latest build, the rollback will fail to find them.

## dnf - Downgrade a Package

Install the highest version lower than the one currently installed.

```
dnf downgrade <package>
```

Downgrade to a specific version instead — list the available versions first, since only what the repositories still carry can be reached:

```
dnf --showduplicates list <package>
dnf downgrade <package>-<version>-<release>
```

## dnf - Pin a Package Version with versionlock

Freeze a package at its current version so ordinary upgrades skip it. Needed for databases, agents and kernels that must not move outside a maintenance window.

```
dnf install python3-dnf-plugin-versionlock
dnf versionlock add <package>
```

Lock to an explicit version, list the active locks, and remove them:

```
dnf versionlock add <package>-<version>-<release>
dnf versionlock list
dnf versionlock delete <package>
dnf versionlock clear
```

`exclude` is the inverse: it blocks a specific known-bad build while leaving the rest available.

```
dnf versionlock exclude <package>-<version>-<release>
```

DNF4 keeps the locks in the file named by `locklist` in `/etc/dnf/plugins/versionlock.conf`; DNF5 replaced this with a TOML file at `/etc/dnf/versionlock.toml`, so a lock list cannot simply be copied from a RHEL 9 host to a Fedora 41 host.

## dnf - Mark Packages as User-Installed or as a Dependency

Change how `autoremove` treats a package without reinstalling it. Marking a package user-installed protects it from being cleaned up when whatever pulled it in goes away.

```
dnf mark install <package>
```

Mark a package as a mere dependency so it becomes eligible for autoremove once nothing needs it:

```
dnf mark remove <package>
```

DNF5 renamed both subcommands to describe the resulting state rather than the action:

```
dnf5 mark user <package>
dnf5 mark dependency <package>
```

## dnf - Remove Orphaned Dependencies

Remove packages that were installed as dependencies and are no longer required by anything user-installed.

```
dnf autoremove
```

Preview the list before running it:

```
dnf list --autoremove
```

`dnf remove` already cleans up unused dependencies by default via `clean_requirements_on_remove`. Turn that off for a single transaction when the dependents must be kept:

```
dnf remove --setopt=clean_requirements_on_remove=0 <package>
```

Run `autoremove` with care on servers built by hand: anything installed before the mark data existed, or installed by a tool that did not mark it, can be swept up.

## dnf - Manage the Metadata Cache

Delete all cached metadata and packages. This is the first thing to try when dnf reports checksum errors or keeps serving a stale package list.

```
dnf clean all
```

Clean selectively — `expire-cache` just marks metadata stale so the next command refetches it, which is much cheaper than discarding everything:

```
dnf clean expire-cache
dnf clean metadata
dnf clean packages
dnf clean dbcache
```

Pre-download metadata so the next transaction is fast, which is what the packaged systemd timer does:

```
dnf makecache
dnf makecache --timer
```

Force a refresh for one command, or forbid network access entirely and work from the cache:

```
dnf --refresh upgrade
dnf -C list --installed
```

DNF4 caches under `/var/cache/dnf`; DNF5 uses its own libdnf5 cache directory, so clearing one does not clear the other on a host that has both.

## dnf - Download Packages Without Installing

Fetch RPMs to the current directory, for staging into an air-gapped environment or for inspection.

```
dnf download <package>
```

Include the dependencies that are missing from the system, and choose the output directory:

```
dnf download --resolve --destdir=/var/tmp/rpms <package>
```

Print the URLs instead of downloading, or fetch the source RPM:

```
dnf download --url <package>
dnf download --source <package>
```

`--downloadonly` is different: it resolves the *full transaction* dnf would perform and downloads exactly those packages, which is how to stage an upgrade during the day and apply it in the maintenance window:

```
dnf upgrade --downloadonly
dnf install --downloadonly --destdir=/var/tmp/rpms <package>
```

On DNF5 the source-RPM option was renamed:

```
dnf5 download --srpm <package>
```

## dnf - Run Non-Interactively in Scripts

Answer yes to every prompt. Required for any unattended run, and it also accepts the GPG key import prompt, so import keys explicitly beforehand if that matters.

```
dnf -y install <package>
```

Answer no to every prompt — the safe way to see a full transaction summary without any chance of applying it:

```
dnf install --assumeno <package>
```

Quieten the output to just the relevant content, and disable a misbehaving plugin for one run:

```
dnf -q -y upgrade
dnf --disableplugin=<plugin> upgrade
```

## dnf - Override Configuration with setopt

Override any `dnf.conf` or repository option for a single command, without editing files.

```
dnf --setopt=install_weak_deps=False install <package>
```

Skipping weak dependencies (`Recommends`) is the usual way to keep container and minimal-server images small. Other options worth overriding per-transaction:

```
dnf --setopt=tsflags=nodocs install <package>
dnf --setopt=keepcache=1 install <package>
dnf --setopt=installonly_limit=2 upgrade
```

Prefix the option with a repository ID — globs allowed — to scope it to that repository:

```
dnf --setopt=<repoid>.skip_if_unavailable=1 upgrade
dnf --setopt='*-debuginfo.gpgcheck=0' install <package>
```

To make an override permanent, DNF4 writes it back with `--save`, while DNF5 uses the `setopt` subcommand:

```
dnf config-manager --save --setopt='*-debuginfo.gpgcheck=0'
dnf5 config-manager setopt '*-debuginfo.pkg_gpgcheck=0'
```

## dnf - Control Dependency Resolution Failures

`--best` forces dnf to use the highest available version or fail outright, rather than quietly settling for an older one that resolves. Use it when a "successful" upgrade that silently skipped a security fix would be worse than an error.

```
dnf --best upgrade
```

DNF4 defaults `best` to false; DNF5 defaults it to true. So the flag that needs writing down differs by generation:

```
dnf --nobest install <package>
dnf5 install --no-best <package>
```

`--skip-broken` drops the packages that cannot be resolved and proceeds with the rest. It is a way to make progress on a partially broken host, not a fix — check afterwards what was skipped:

```
dnf --skip-broken upgrade
```

`--allowerasing` permits dnf to *remove* installed packages in order to satisfy the transaction. It is the flag that resolves conflicting-provider deadlocks, and also the flag most likely to uninstall something important, so always read the summary before confirming:

```
dnf --allowerasing install <package>
```

DNF5 adds `--skip-unavailable` for the separate case of arguments that match nothing at all:

```
dnf5 install --skip-unavailable <package> <package>
```

## dnf - Operate on Another Root

Run the whole transaction against a directory tree instead of the running system — for building images, or for repairing a broken host from rescue media. The path must be absolute.

```
dnf --installroot=/mnt/sysimage --releasever=9 install <package>
```

`--releasever` is required because dnf cannot detect the release from an empty or foreign root, and `$releasever` appears in almost every repository URL. By default the configuration, repositories and keys are read from inside the installroot; DNF5 can be told to use the host's configuration instead:

```
dnf5 --installroot=/mnt/sysimage --use-host-config upgrade
```

Query the other root's RPM database directly:

```
rpm --root=/mnt/sysimage -qa
```

## dnf - Check Whether a Restart Is Needed

Report whether a reboot is required after patching. Exit code 1 means a reboot is recommended, 0 means it is not — which makes it directly usable in a patching playbook.

```
dnf install dnf-plugins-core
dnf needs-restarting -r
```

List the systemd services running against files that have been replaced on disk, so they can be restarted instead of rebooting the host:

```
dnf needs-restarting -s
```

Show the affected processes, restricted to the current user's if wanted:

```
dnf needs-restarting
dnf needs-restarting -u
```

On DNF5 the command no longer scans for open files; it behaves like DNF4's `--reboothint` by default, and `-r` is accepted only for compatibility. Process-level detail moved to `--processes`:

```
dnf5 needs-restarting --services
dnf5 needs-restarting --processes
```

## dnf - Query the RPM Database Directly

`rpm` reads the local package database with no dependency solving and no network, so it is the right tool for inventory and for answering questions on a host whose repositories are unreachable.

```
rpm -qa
```

Inspect a single installed package — its metadata, its file list, and just its config files:

```
rpm -qi <package>
rpm -ql <package>
rpm -qc <package>
```

Find the owning package of a file that is already installed, or the packages providing a capability:

```
rpm -qf /usr/sbin/sshd
rpm -q --whatprovides <capability>
```

Produce machine-readable inventory, which is the usual input for a fleet-wide package report:

```
rpm -qa --qf '%{NAME} %{VERSION}-%{RELEASE}.%{ARCH} %{INSTALLTIME:date}\n'
```

Read the packaged changelog to confirm a backported fix is present — RHEL backports patches without bumping the upstream version, so the version number alone does not answer the question:

```
rpm -q --changelog <package> | head -n 40
```

## dnf - Verify Installed Package Integrity

Compare the files on disk against the metadata recorded at install time. Silence means everything matches.

```
rpm -V <package>
```

Verify every installed package. This is slow on a large host but is a useful integrity baseline and a quick way to find files edited outside configuration management:

```
rpm -Va
```

Each result line is a nine-character mask, one character per failed check, followed by an attribute marker and the path. `S` size, `M` mode, `5` digest, `D` device, `L` symlink target, `U` owner, `G` group, `T` mtime, `P` capabilities; `.` means the check passed and `?` means it could not be performed. A `c` in the attribute column marks a config file, so `S.5....T.  c /etc/ssh/sshd_config` is an edited config and normally expected.

Restrict the verification to the checks that matter, for example skipping the expensive digest pass:

```
rpm -Va --nofiledigest
```

Verification reads the local RPM database, so it detects accidental damage but not a compromise that also rewrote the database. Treat it as a change-detection tool, not as tamper-proof attestation.
