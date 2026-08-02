# Lynis

Lynis is a security auditing and hardening tool for Unix-based systems. It runs hundreds of tests against a running host, reports findings and suggestions, and produces a hardening index that can be tracked over time.

#platform/multiple #target/Linux #cat/Security

% lynis, security, auditing, hardening, compliance

## Lynis - Audit the System

Run a full audit of the host. Run it as root, otherwise many tests are skipped for lack of access.

```
sudo lynis audit system
```

Lynis pauses between sections by default; skip the prompts for an unattended run:

```
sudo lynis audit system --quick
```

## Lynis - Run from Cron

Run in fully non-interactive mode, with no colours and no pauses, which is the mode intended for scheduled audits.

```
sudo lynis audit system --cronjob
```

Combine with an explicit report path so each run is kept separately:

```
sudo lynis audit system --cronjob --report-file /var/log/lynis/$(date +%F).dat
```

## Lynis - Audit a Dockerfile

Scan a Dockerfile for security issues without running the image.

```
lynis audit dockerfile Dockerfile
```

## Lynis - Run Specific Tests

Run only the listed test IDs, which is far faster than a full audit when re-checking one finding.

```
sudo lynis audit system --tests "AUTH-9262 AUTH-9286"
```

## Lynis - Run Tests by Group

Restrict the audit to one or more test groups, such as the firewall or SSH checks.

```
sudo lynis audit system --tests-from-group "firewalls ssh"
```

List the groups that are available:

```
lynis show groups
```

## Lynis - Run Tests by Category

Restrict the audit to a category. The categories are `security`, `privacy`, and `performance`.

```
sudo lynis audit system --tests-from-category "security"
```

List the categories:

```
lynis show categories
```

## Lynis - Show Only Warnings

Suppress the informational output and print just the warnings.

```
sudo lynis audit system --quick --warnings-only
```

## Lynis - Locate the Log and Report Files

Lynis writes a human-readable log and a machine-readable report. Ask it where they are rather than assuming, since the paths change when it runs unprivileged.

```
lynis show logfile
```

Show the report path:

```
lynis show report
```

As root these default to `/var/log/lynis.log` and `/var/log/lynis-report.dat`; unprivileged runs fall back to the home directory.

## Lynis - Read the Hardening Index

The hardening index is a 0-100 score summarising the audit. Pull it out of the report file to track it between runs.

```
grep hardening_index /var/log/lynis-report.dat
```

Extract every suggestion instead:

```
grep '^suggestion\[\]=' /var/log/lynis-report.dat
```

List the warnings:

```
grep '^warning\[\]=' /var/log/lynis-report.dat
```

## Lynis - Write the Report Elsewhere

Override the report and log destinations, for example to collect results on a shared volume.

```
sudo lynis audit system --quick --report-file /tmp/report.dat --log-file /tmp/lynis.log
```

Discard the log entirely:

```
sudo lynis audit system --quick --no-log
```

## Lynis - Record the Auditor

Stamp the report with the name of the person or system running the audit, for compliance evidence.

```
sudo lynis audit system --auditor "Security Team"
```

## Lynis - Run in Pentest Mode

Run as a non-privileged user, skipping the tests that require root. Useful when auditing a host you do not own.

```
lynis audit system --pentest
```

## Lynis - Use a Custom Profile

Run against a specific profile, which is how test exclusions and site policy are applied.

```
sudo lynis audit system --profile /etc/lynis/custom.prf
```

List the profiles Lynis found:

```
lynis show profiles
```

Show the settings those profiles resolve to:

```
lynis show settings
```

## Lynis - List Available Tests

Print every test Lynis knows about.

```
lynis show tests
```

Show the details of the current environment and detected OS:

```
lynis show os
```

## Lynis - Generate systemd Units

Emit systemd service and timer units for running Lynis on a schedule.

```
lynis generate systemd-units
```

Generate the host identifiers used to correlate uploads:

```
lynis generate hostids
```

## Lynis - Upload Results

Send the report to a central Lynis collector, configured in the profile.

```
sudo lynis audit system --cronjob --upload
```

Upload a report that was generated earlier without re-running the audit:

```
sudo lynis upload-only
```

## Lynis - Check for Updates

Show whether the installed version is current and when it was released.

```
lynis update info
```

Show just the version:

```
lynis show version
```

Show the release date, useful for spotting an outdated packaged copy:

```
lynis show releasedate
```

## Lynis - Get Help

List the top-level commands.

```
lynis show commands
```

List every command-line option:

```
lynis show options
```

Open the manual page:

```
lynis show man
```
