# pacman

pacman is the package manager of Arch Linux and its derivatives. It installs, upgrades, queries, and removes binary packages, resolves their dependencies, and verifies their OpenPGP signatures against a local keyring.

#platform/multiple #target/Arch #cat/PackageManagement

% pacman, arch, packages, aur, makepkg, pacman-key, paccache, pactree, checkupdates, rolling release

## pacman - Understand the Operation Letters

pacman takes one capital operation letter first, then lower-case sub-options that only exist inside that operation. This is the single biggest source of confusion for people coming from apt or dnf, where each action is a subcommand word. The same lower-case letter means different things under different operations: `-s` is "search" under `-S` and `-Q`, but "recursive" under `-R`.

```
pacman -S <package>     # sync: install or upgrade from a configured repository
pacman -Q               # query: read the local database of installed packages
pacman -R <package>     # remove: delete an installed package
pacman -U <file>        # upgrade: install a package file or URL, not a repo name
pacman -D <package>     # database: change stored metadata such as install reason
pacman -F <file>        # files: search the remote file lists of sync repositories
pacman -T <depspec>     # deptest: report which of the given dependencies are unmet
```

Every operation prints its own sub-options, which is faster than paging the man page:

```
pacman -S --help
pacman -Q --help
```

## pacman - Perform a Full System Upgrade

Arch is a rolling release, so there is no separate "update the index" and "upgrade" step. `-y` refreshes the sync databases and `-u` upgrades every out-of-date package; they are meant to be used together in one transaction.

```
pacman -Syu
```

Upgrade the system and install additional packages in the same transaction, which is the correct way to install something when the databases are stale:

```
pacman -Syu <package>
```

Force a re-download of every sync database even if it looks current, which is only needed when a mirror is serving inconsistent metadata:

```
pacman -Syyu
```

Before upgrading a production host, read the Arch news feed. Upgrades that need manual intervention are announced there, and pacman will not warn you in advance.

## pacman - Avoid Partial Upgrades

Partial upgrades are unsupported on Arch. When a library gets a soname bump, maintainers rebuild every dependent package in the repositories at the same time, so refreshing the database and then pulling in a single package will link new binaries against libraries the rest of the system does not have yet. Never run these:

```
pacman -Sy                       # refreshes the database without upgrading
pacman -Sy <package>             # installs against a database the system does not match
pacman -Sy && pacman -S <pkg>    # same thing, spread over two commands
pacman -Syuw                     # syncs the database but only downloads, does not install
```

Always refresh and upgrade in the same transaction instead:

```
pacman -Syu <package>
```

If `pacman -Syu` fails partway, the `-Sy` half has already succeeded, so the machine is now in a partial-upgrade state. Resolve the error and finish the upgrade before running any other package operation.

## pacman - Install Packages

Install one or more packages from the configured repositories, pulling in dependencies. Reinstalling uses the same command.

```
pacman -S <package> <package>
```

Pin the repository when the same package name exists in more than one, for example to take the stable version rather than the testing one:

```
pacman -S extra/<package>
```

Skip targets that are already installed and current, which makes provisioning scripts idempotent instead of forcing a pointless reinstall:

```
pacman -S --needed <package>
```

Install something as a dependency rather than an explicit request, so it will be cleaned up as an orphan once nothing needs it:

```
pacman -S --asdeps <package>
```

Print the targets instead of acting, which is the closest thing pacman has to a dry run:

```
pacman -Sp --print-format '%n %v' <package>
```

## pacman - Install a Package File with -U

`-U` installs a package file or URL directly rather than a name resolved from a repository. This is how locally built and AUR packages get onto the system; its dependencies are still pulled from the sync repositories.

```
pacman -U /path/to/<package>-<version>-<arch>.pkg.tar.zst
```

Install straight from a URL:

```
pacman -U https://example.com/repo/<package>-<version>-<arch>.pkg.tar.zst
```

Use a `file://` URL to have pacman keep a copy in its cache, so the package can be reinstalled later without rebuilding it:

```
pacman -U file:///path/to/<package>-<version>-<arch>.pkg.tar.zst
```

## pacman - Remove Packages

The remove flags stack, and each letter removes strictly more than the last. Knowing exactly what each one deletes matters, because `-R` alone is what leaves orphans behind on long-lived servers.

```
pacman -R <package>     # the package only; its dependencies stay behind
pacman -Rs <package>    # also its dependencies, if nothing else needs them and
                        # they were not explicitly installed by a user
pacman -Rn <package>    # the package only, and no .pacsave backups are kept
pacman -Rns <package>   # dependencies as above, and no .pacsave backups
```

Remove a package together with everything that depends on it. This is recursive and can take out a large part of the system, so read the confirmation list:

```
pacman -Rsc <package>
```

Remove a group while skipping members that other packages still need, instead of aborting:

```
pacman -Rsu <group>
```

Avoid `pacman -Rdd`, which skips dependency checks entirely and will happily remove something the rest of the system links against.

## pacman - Search the Repositories

Search names and descriptions in the sync databases using an extended regular expression. Multiple terms are ANDed.

```
pacman -Ss <regex>
```

Anchor the expression to keep it from matching every description on the mirror:

```
pacman -Ss '^nginx-'
```

Print names only, which is what you want when feeding the result into another command:

```
pacman -Ssq <regex>
```

List every package in a repository, useful for auditing what an added third-party repo actually ships:

```
pacman -Sl <repository>
```

## pacman - Search Installed Packages

The same search, but against the local database rather than the mirrors, so it answers "is this already on the box".

```
pacman -Qs <regex>
```

List every installed package with its version, which is the standard way to snapshot a machine's inventory:

```
pacman -Q
```

Names only, suitable for diffing two hosts:

```
pacman -Qq
```

## pacman - Show Package Information

Show the metadata of a package in the repositories, including its dependencies, optional dependencies, and download size, before installing it.

```
pacman -Si <package>
```

Show the same for an already installed package, from the local database, so it works offline:

```
pacman -Qi <package>
```

Pass `-i` twice to also list the package's backup files and whether they have been modified. This is how to find out which config files pacman is tracking and will turn into `.pacnew` on upgrade:

```
pacman -Qii <package>
```

Show which installed packages depend on a given one by passing `-i` twice to the sync query:

```
pacman -Sii <package>
```

## pacman - List the Files a Package Installs

List every file owned by an installed package, which is the quickest way to find where a daemon's unit file or default config landed.

```
pacman -Ql <package>
```

Filter to just the binaries it puts on PATH:

```
pacman -Ql <package> | grep -E 'bin/.+'
```

Verify that all of a package's files are still present on disk, and pass `-k` twice to also check permissions, sizes, and modification times:

```
pacman -Qkk <package>
```

## pacman - Find Which Package Owns a File

Given a path on disk, report which installed package owns it. This is the first thing to run when investigating an unexpected file or a file conflict during an upgrade.

```
pacman -Qo /path/to/file
```

Works on anything resolvable through PATH as well:

```
pacman -Qo $(which <command>)
```

If a file is owned by nothing, it was installed outside pacman and should be removed by hand before the conflicting package can be upgraded.

## pacman - Search the Files Database for a Missing Command

`-Qo` only knows about installed packages. To find which package in the repositories *would* provide a file you do not have yet, use the files database. It is a separate database and is not refreshed by `-Sy`, so sync it first.

```
pacman -Fy
```

Then look up the file:

```
pacman -F <filename>
pacman -F /usr/bin/<command>
```

List the files a remote, not-yet-installed package would install:

```
pacman -Fl <package>
```

Treat the query as a regular expression:

```
pacman -Fx '<regex>'
```

Enabling `pacman-filesdb-refresh.timer` from pacman-contrib keeps the files database current on its own.

## pacman - List Explicitly Installed Packages

Split the local database by install reason. Explicit packages are the ones somebody actually asked for; everything else was pulled in as a dependency. This distinction is what makes orphan cleanup possible.

```
pacman -Qe     # explicitly installed
pacman -Qd     # installed as a dependency
```

List explicitly installed packages that nothing else requires. This is the minimal set that describes a machine, and is what to check into configuration management:

```
pacman -Qqet
```

Restrict to packages that came from the repositories, excluding anything built locally:

```
pacman -Qqen
```

## pacman - Find and Remove Orphans

Orphans are packages installed as a dependency that nothing requires any more. They accumulate whenever `pacman -R` is used instead of `-Rs`, or when a package drops a dependency in a new version.

```
pacman -Qdt
```

Remove them recursively, without leaving `.pacsave` files behind. Piping is the form the wiki recommends; if there are no orphans it prints `error: argument '-' specified with empty stdin`, which is harmless:

```
pacman -Qdtq | pacman -Rns -
```

The command-substitution form does the same thing, but fails with a usage error when the list is empty, so it is the worse choice inside a script:

```
pacman -Rns $(pacman -Qdtq)
```

To keep an orphan permanently, flip its install reason to explicit with the `-D` operation instead of excluding it by hand every time:

```
pacman -D --asexplicit <package>
```

Note that `-Qdt` lists true orphans only. Pass `-t` twice to also catch packages that are merely an optional dependency of something else.

## pacman - List Foreign and AUR Packages

Foreign packages are installed packages that no configured sync repository knows about, which on a real server means AUR builds, in-house packages, and packages that were dropped from the official repositories.

```
pacman -Qm
```

Names only, which is the list you must rebuild by hand after a soname bump because `pacman -Syu` will never touch them:

```
pacman -Qmq
```

The inverse, packages that do come from a repository:

```
pacman -Qn
```

## pacman - Clean the Package Cache

pacman keeps every downloaded package in `/var/cache/pacman/pkg/` forever and never prunes it, which is a common cause of a full root filesystem on long-lived hosts. Those files are also what makes offline reinstalls and downgrades possible, so do not empty the cache wholesale.

The safe tool is `paccache` from pacman-contrib, which keeps the three most recent versions of each package by default:

```
paccache -r
```

Preview what it would delete first:

```
paccache -dv
```

Keep only one previous version, or purge only the cached versions of packages that are no longer installed:

```
paccache -rk1
paccache -ruk0
```

pacman's own cleaning is more aggressive because it cannot keep a version window. `-Sc` drops cached packages that are not currently installed plus unused sync databases; `-Scc` empties the cache completely and leaves you unable to reinstall or downgrade without a network:

```
pacman -Sc
pacman -Scc
```

Enabling `paccache.timer` runs the safe cleanup weekly.

## pacman - Download Packages Without Installing

Fetch packages into the cache without touching the running system, for example to stage an upgrade on a host with a maintenance window, or to seed an internal mirror.

```
pacman -Sw <package>
```

Do not reach for `pacman -Syuw` to pre-download a full upgrade: it refreshes the sync database without installing anything, which leaves the machine in exactly the partial-upgrade state described above. Use `checkupdates -d` instead, which downloads to the cache against a temporary database.

## pacman - Reinstall and Overwrite Conflicting Files

Reinstalling is just `-S` on an already-installed package; the install reason is preserved.

```
pacman -S <package>
```

Reinstall every native package while keeping install reasons, which repairs a system whose files were damaged out from under the database:

```
pacman -Qnq | pacman -S -
```

When an upgrade aborts with `<file> exists in filesystem`, first find out who owns the file with `pacman -Qo`. Only if it is owned by nothing, and after renaming or removing it is not an option, force the overwrite with a glob:

```
pacman -S --overwrite '/usr/lib/<library>*' <package>
```

`--overwrite` bypasses file conflict checks, which is a safety feature doing its job. On a properly maintained system it should only be used when the Arch developers explicitly say so; careless use is a known cause of a corrupted initramfs and an unbootable host.

## pacman - Skip a Package During Upgrade

Hold a package back for a single upgrade with a comma-separated list on the command line.

```
pacman -Syu --ignore <package>,<package>
```

Make the hold persistent by adding it to the `[options]` section of `/etc/pacman.conf`. Glob patterns are allowed, and multiple `IgnorePkg` lines are additive:

```
IgnorePkg = linux linux-headers
IgnorePkg = nvidia*
IgnoreGroup = gnome
```

Holding packages is a deliberate partial upgrade, so it carries the same risk. It is defensible for a kernel pinned to an out-of-tree module, and rarely defensible for a library. An ignored package can still be upgraded explicitly with `pacman -S <package>`, and pacman will remind you that it was on the ignore list.

## pacman - Handle .pacnew and .pacsave Files

When a package ships a new version of a config file that you have edited, pacman refuses to overwrite your copy and writes the new one alongside it as `.pacnew`. When a package with a tracked config file is removed, your copy is kept as `.pacsave`. Neither is ever merged automatically, and ignoring them is how a service ends up running on a config that no longer matches the software.

Find them after an upgrade:

```
find /etc -name '*.pacnew' -o -name '*.pacsave'
```

Review the whole history from pacman's log, which also catches ones already dealt with:

```
grep -E '\.pacnew|\.pacsave' /var/log/pacman.log
```

Merge them interactively with `pacdiff` from pacman-contrib, which uses the backup arrays in the local database and defaults to vimdiff:

```
pacdiff
DIFFPROG=meld pacdiff
```

Never blindly copy a `.pacnew` over the live file. Diff it, port your local changes forward, then delete the `.pacnew`. Use `pacman -R -n` to suppress `.pacsave` creation when removing a package whose config you know you do not want back.

## pacman - Fix Keyring and Signature Errors

Package signatures are checked against a local keyring, so a machine that has not been upgraded in months will fail verification with `invalid or corrupted package (PGP signature)` or `signature ... is unknown trust` simply because its `archlinux-keyring` is too old to know the current packager keys.

The supported fix is to sync the database and upgrade the keyring alone, then upgrade the system. Both halves must run back to back; this is explicitly not treated as a partial upgrade:

```
pacman -Sy --needed archlinux-keyring && pacman -Su
```

Refresh the keys already in the keyring from the configured keyservers. A message about your own local key not being found is expected:

```
pacman-key --refresh-keys
```

If the keyring itself is broken, reset it completely by removing `/etc/pacman.d/gnupg` and re-importing the distribution keys:

```
pacman-key --init
pacman-key --populate
```

Also check the clock. Signature verification depends on the system time, so a host with a wrong date will reject valid signatures as expired.

## pacman - Clear a Stale Database Lock

pacman creates `/var/lib/pacman/db.lck` before altering the database so two instances cannot run at once. If a transaction is killed, the lock survives and every later run fails with `failed to init transaction (unable to lock database)`.

Confirm nothing is actually holding it before deleting it, which matters on a server where an unattended-upgrade timer may be mid-transaction:

```
fuser /var/lib/pacman/db.lck
```

If no process is using it, remove the stale lock:

```
rm /var/lib/pacman/db.lck
```

## pacman - Inspect Dependency Trees

`pactree`, from pacman-contrib, renders the dependency graph that `-Qi` only summarises.

```
pactree <package>
```

Reverse the direction to see what depends on the package, which is the check to run before removing anything on a production host:

```
pactree -r <package>
```

Limit the depth, or flatten the output to one unique name per line for scripting:

```
pactree -d 1 <package>
pactree -u <package>
```

Include optional dependencies, and read from the sync databases so it works on packages that are not installed yet:

```
pactree -o <package>
pactree -s <package>
```

## pacman - Check for Updates Without Syncing the Database

`pacman -Qu` only reports upgrades relative to whatever the sync database currently holds, which tempts people into running `-Sy` first and creating a partial upgrade. `checkupdates` from pacman-contrib avoids that entirely by syncing a private temporary database, leaving the system's own database untouched.

```
checkupdates
```

It exits 2 when there is nothing to do, which makes it usable directly in monitoring checks:

```
checkupdates || echo "no updates pending"
```

Pre-download the pending updates into pacman's cache without touching the system database, so the later `pacman -Syu` runs with no network transfer inside the maintenance window:

```
checkupdates -d
```

## pacman - Build a Package from the AUR

The AUR distributes build recipes, not binaries. `makepkg` builds a package file from a PKGBUILD and pacman installs the result, so AUR packages show up as foreign packages afterwards and are never upgraded by `pacman -Syu`. Install `base-devel` first.

```
git clone https://aur.archlinux.org/<package>.git
cd <package>
```

Read the PKGBUILD and the `.install` file before building. They run as arbitrary shell code, and AUR content is unvetted user submissions.

Build and install in one step. `-s` resolves and installs missing build and runtime dependencies with pacman, `-i` installs the finished package, `-r` removes the build-only dependencies afterwards, and `-c` cleans the work tree:

```
makepkg -sirc
```

Never run `makepkg` as root. To update later, pull the repository and rebuild:

```
git pull && makepkg -sirc
```

## pacman - Configure /etc/pacman.conf

The `[options]` section holds global behaviour and every other section defines a repository. Repository order is significant: a package present in two repositories is taken from whichever is listed first, regardless of version.

```
[options]
ParallelDownloads = 5
Color
VerbosePkgLists
CheckSpace
IgnorePkg   = linux
CacheDir    = /var/cache/pacman/pkg/
SigLevel    = Required DatabaseOptional

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist
```

`ParallelDownloads` sets how many packages download concurrently; if the directive is absent, downloads run one at a time. Enable 32-bit support by uncommenting the `[multilib]` section and then running a full upgrade:

```
[multilib]
Include = /etc/pacman.d/mirrorlist
```

Never symlink the cache directory. Point `CacheDir` at the new location or bind-mount it, because pacman recreates that path during self-upgrade and will destroy a symlink.

Dump the configuration as pacman actually resolves it, with `Include` directives expanded, which is the reliable way to audit a host's repositories:

```
pacman-conf
pacman-conf --repo-list
pacman-conf -r core
```
