# apt

apt is the high-level package manager for Debian and Ubuntu. It resolves dependencies, fetches `.deb` archives from configured repositories, and drives `dpkg` to unpack and configure them.

#platform/multiple #target/Debian #cat/PackageManagement

% apt, debian, ubuntu, packages, dpkg, apt-get, repositories, dependencies

## apt - Update the Package Index

Download the package lists from every configured source into `/var/lib/apt/lists`. This only refreshes metadata; it never installs or upgrades anything. It is a separate step because every other apt command reads the cached index offline, so a stale index means apt will not see new versions and will try to fetch `.deb` files that the mirror has already deleted.

```
sudo apt update
```

Refresh and report how many packages have upgrades pending, without acting:

```
sudo apt update && apt list --upgradable
```

## apt - Upgrade Installed Packages

Install the newest version of everything already installed. `apt upgrade` will pull in new packages when a dependency requires it, but it will never remove an installed package. Any upgrade that would require a removal is skipped and reported as "kept back".

```
sudo apt upgrade
```

`apt-get upgrade` is stricter still: it neither removes nor installs anything new.

```
sudo apt-get upgrade
```

Upgrade a single package and its dependencies without touching the rest of the system:

```
sudo apt install --only-upgrade <package>
```

## apt - Perform a Full Upgrade

`full-upgrade` (`dist-upgrade` under `apt-get`) does everything `upgrade` does, but is also allowed to remove installed packages to resolve changed dependencies. This is what clears the "kept back" list, and it is why it should never be run unattended on a production host without reading the plan first.

```
sudo apt full-upgrade
```

The `apt-get` spelling, still the one used in most scripts and documentation:

```
sudo apt-get dist-upgrade
```

## apt - Simulate Before Acting

Print the exact set of installs, removals, and upgrades apt would perform, and change nothing. This works without root, so it is safe to run on a production box before scheduling a maintenance window. Use it on every `full-upgrade`, `autoremove`, and `remove` before committing.

```
apt-get -s full-upgrade
```

`-s` has several equivalent spellings; `--dry-run` is the readable one for scripts:

```
apt-get --dry-run install <package>
```

Simulate a removal to see what depends on the package and would be dragged out with it:

```
apt-get -s remove <package>
```

## apt - Install a Package

Install a package and everything it depends on.

```
sudo apt install <package>
```

Skip the `Recommends` field, which is what keeps container images and minimal servers small:

```
sudo apt install --no-install-recommends <package>
```

Install a local `.deb` and let apt resolve its dependencies from the repositories, which `dpkg -i` cannot do:

```
sudo apt install ./<package>.deb
```

Reinstall a package whose files have been damaged, without changing its version:

```
sudo apt install --reinstall <package>
```

## apt - Install a Specific Version

Pin an install to an exact version string. This is the reliable way to keep a fleet on a known-good build; the version must still be present in a configured repository.

```
sudo apt install <package>=<version>
```

List the versions actually available before choosing one:

```
apt-cache madison <package>
```

Installing an older version than the one installed is a downgrade and must be allowed explicitly:

```
sudo apt install --allow-downgrades <package>=<version>
```

## apt - Remove or Purge a Package

`remove` deletes the package's files but leaves its configuration under `/etc` in place, so reinstalling later restores the old settings. The package stays in the dpkg database in the `rc` state.

```
sudo apt remove <package>
```

`purge` additionally deletes the conffiles that dpkg tracks — mostly `/etc` — leaving no trace in the dpkg database. It does not touch data written at runtime by the service, such as databases under `/var/lib`, nor anything in home directories.

```
sudo apt purge <package>
```

List packages that are removed but still hold configuration, so leftovers can be cleaned up:

```
dpkg -l | grep '^rc'
```

Purge every one of them:

```
dpkg -l | awk '/^rc/ {print $2}' | xargs -r sudo apt purge -y
```

## apt - Remove Unused Dependencies

Remove packages that were pulled in automatically and are no longer required by anything manually installed. On long-lived servers this is mainly what reclaims `/boot` space from old kernels. Always simulate first — a package wrongly marked automatic will be swept up.

```
apt-get -s autoremove
sudo apt autoremove
```

Remove and purge their configuration in one step:

```
sudo apt autoremove --purge
```

## apt - Search for a Package

Full-text search over package names and descriptions.

```
apt search <term>
```

Restrict the match to the package name, which cuts most of the noise:

```
apt search --names-only <regex>
```

`apt-cache search` is the equivalent that produces stable, script-friendly output; `apt` itself warns that its CLI is not a stable interface.

```
apt-cache search <term>
```

## apt - Show Package Details

Show the description, dependencies, size, and origin of a package.

```
apt show <package>
```

Show every available version record rather than just the candidate:

```
apt-cache show <package>
```

List what a package depends on, and what depends on it:

```
apt-cache depends <package>
apt-cache rdepends --installed <package>
```

## apt - Inspect Versions and Pinning

`apt-cache policy` prints the installed version, the candidate apt would install, and the priority of every source offering the package. It is the first command to run when apt installs an unexpected version or refuses to upgrade — the priority column shows exactly which repository or pin won.

```
apt-cache policy <package>
```

With no argument it dumps the priority of every configured source, which is how to confirm a `preferences.d` file is being applied:

```
apt-cache policy
```

## apt - List Packages

List everything installed on the system.

```
apt list --installed
```

List only what has a pending upgrade:

```
apt list --upgradable
```

Show every version available for a package across all sources:

```
apt list --all-versions <package>
```

Filter with a glob pattern:

```
apt list --installed 'linux-image-*'
```

`dpkg -l` gives the same view with the state flags, where a leading `ii` means installed and configured:

```
dpkg -l <package>
```

## apt - Find Which Package Provides a File

Look up the owner of a file that is already on disk. This is a local dpkg database query and needs no network access.

```
dpkg -S /usr/bin/curl
```

To search files in packages that are *not* installed, `apt-file` is needed. It is not installed by default and maintains its own index, so it must be set up before first use.

```
sudo apt install apt-file
sudo apt-file update
apt-file search <path-fragment>
```

## apt - List the Files a Package Installs

Print every path shipped by an installed package — the quickest way to find a daemon's unit file or its default config.

```
dpkg -L <package>
```

Narrow it to the config files:

```
dpkg -L <package> | grep '^/etc'
```

Verify that the installed files still match the package's recorded checksums:

```
sudo debsums -c <package>
```

## apt - Hold a Package at a Version

Mark a package so apt will not automatically upgrade, install, or remove it. On on-premise servers this is how a database or kernel is frozen at a validated version while the rest of the system keeps receiving security updates.

```
sudo apt-mark hold <package>
```

Release the hold:

```
sudo apt-mark unhold <package>
```

Audit the holds on a host — this should be part of any build report, because a forgotten hold silently stops security patches:

```
apt-mark showhold
```

Holds are stored as dpkg selections, so they can also be applied in bulk:

```
echo "<package> hold" | sudo dpkg --set-selections
```

## apt - List Manually and Automatically Installed Packages

Print the packages an operator explicitly asked for. This is the useful input for rebuilding a host or writing an Ansible package list, since it excludes the dependency closure.

```
apt-mark showmanual
```

Print the packages installed only as dependencies — these are the candidates for `autoremove`:

```
apt-mark showauto
```

Change the mark, for example to protect a package from `autoremove`:

```
sudo apt-mark manual <package>
sudo apt-mark auto <package>
```

## apt - Install Non-Interactively in Scripts

Suppress debconf prompts and answer yes automatically. Without `DEBIAN_FRONTEND=noninteractive` a package such as `tzdata` or `postfix` will block forever waiting on a terminal that a CI job or Ansible run does not have.

```
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y <package>
```

Also decide the conffile conflict policy up front, otherwise an upgrade stops to ask whether to keep the local `/etc` file. `--force-confold` keeps the existing file; `--force-confdef` lets dpkg take the default action where one is defined.

```
sudo DEBIAN_FRONTEND=noninteractive apt-get -y \
  -o Dpkg::Options::="--force-confold" \
  -o Dpkg::Options::="--force-confdef" \
  install <package>
```

Use `apt-get`, not `apt`, in scripts — `apt` explicitly does not guarantee a stable command-line interface between releases.

## apt - Clean the Package Cache

Delete every `.deb` retained in `/var/cache/apt/archives`. Worth doing on hosts with a small root filesystem and at the end of a container build.

```
sudo apt clean
```

Delete only the archives that can no longer be downloaded from any source, keeping the current ones:

```
sudo apt autoclean
```

Check how much the cache is holding before clearing it:

```
du -sh /var/cache/apt/archives
```

## apt - Download a Package Without Installing

Fetch the `.deb` into the current directory without touching the system. This works unprivileged and is how packages are staged for an air-gapped host.

```
apt download <package>
```

Download a specific version:

```
apt download <package>=<version>
```

Fetch a package together with its whole dependency chain into the cache, so a later install runs offline:

```
sudo apt-get install --download-only <package>
```

Fetch the source package instead of the binary:

```
apt-get source <package>
```

## apt - Inspect the Source Lists

Sources live in `/etc/apt/sources.list` and in `/etc/apt/sources.list.d/`. Files ending in `.list` use the legacy one-line format; files ending in `.sources` use the deb822 multi-line format, which apt documents as gradually becoming the default and which Ubuntu 24.04 already uses for the distribution's own repositories.

```
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/
```

The legacy one-line form, still valid:

```
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable
```

The same source in deb822 form, which is easier to template and lets each field be edited independently:

```
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
```

Disable a deb822 source without deleting the file by adding a field, which keeps the configuration under version control:

```
Enabled: no
```

## apt - Add a Third-Party Repository with a Signed Keyring

Store the repository's key in its own file and bind it to that one repository with `Signed-By`. The deprecated `apt-key add` put the key in a global trusted keyring, where it could sign packages for *any* repository — a third-party vendor key would then be trusted to replace core system packages. Never use `apt-key add`.

```
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

If the key is served in binary form rather than ASCII armour, convert it and use a `.gpg` extension:

```
curl -fsSL <key-url> | sudo gpg --dearmor -o /etc/apt/keyrings/<vendor>.gpg
```

Write the source stanza referencing that keyring, then refresh:

```
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```

On Ubuntu, `add-apt-repository` handles PPAs and their keys automatically; `-n` skips the implicit `apt update`:

```
sudo add-apt-repository -n ppa:<owner>/<ppa>
sudo add-apt-repository --remove ppa:<owner>/<ppa>
```

## apt - Pin a Package with Preferences

Drop a file in `/etc/apt/preferences.d/` to override which source apt prefers. Default priorities are 100 for the installed version and 500 for versions from an ordinary source; a pin above 1000 will even force a downgrade. Use this to add a third-party repository for one package without letting it shadow the distribution's packages.

```
sudo tee /etc/apt/preferences.d/99-vendor >/dev/null <<'EOF'
Package: *
Pin: origin download.example.com
Pin-Priority: 100

Package: <package>
Pin: origin download.example.com
Pin-Priority: 700
EOF
```

Freeze a package at a version series, an alternative to `apt-mark hold` that still allows patch updates:

```
Package: <package>
Pin: version 1.28.*
Pin-Priority: 1001
```

Confirm the pin took effect — the candidate line is the answer:

```
apt-cache policy <package>
```

## apt - Fix Broken Dependencies

Report packages with unmet dependencies. This aborts with an error rather than changing anything, so it is safe to run as a health check after a failed install.

```
sudo apt-get check
```

Attempt to repair a system left half-configured, typically after a `dpkg -i` that ignored dependencies or an interrupted upgrade:

```
sudo apt --fix-broken install
```

Finish configuring packages that were unpacked but never configured:

```
sudo dpkg --configure -a
```

List packages dpkg considers to be in a broken state:

```
sudo dpkg --audit
```

## apt - Reconfigure an Installed Package

Re-run a package's debconf configuration without reinstalling it — the supported way to change a locale, timezone, or the ssl-cert defaults after installation.

```
sudo dpkg-reconfigure <package>
```

Ask every question, including the low-priority ones normally answered from defaults:

```
sudo dpkg-reconfigure -plow <package>
```

Preseed answers instead of prompting, so the change can be automated:

```
echo "tzdata tzdata/Areas select Europe" | sudo debconf-set-selections
```

## apt - Enable Unattended Security Upgrades

`unattended-upgrades` applies security updates on a timer without an operator. On a server, enable it for the security pocket only and leave feature upgrades to a change window.

```
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

The two switches that control it live in `/etc/apt/apt.conf.d/20auto-upgrades`; the allowed origins and any package blacklist live in `50unattended-upgrades`:

```
cat /etc/apt/apt.conf.d/20auto-upgrades
cat /etc/apt/apt.conf.d/50unattended-upgrades
```

Test the configuration without applying anything:

```
sudo unattended-upgrade --dry-run --debug
```

## apt - Read the Package History

`/var/log/apt/history.log` records every apt transaction with a timestamp, the command line that triggered it, and the exact package versions installed, upgraded, or removed. This is the record to consult when a host started misbehaving and nobody admits to changing it.

```
less /var/log/apt/history.log
```

Show only what was upgraded, with dates:

```
grep -E '^(Start-Date|Commandline|Upgrade):' /var/log/apt/history.log
```

Older transactions are rotated and compressed, so search the whole set:

```
zgrep -h '<package>' /var/log/apt/history.log*
```

`term.log` alongside it holds the raw dpkg output, which is where a maintainer script's error message will be:

```
sudo less /var/log/apt/term.log
```
