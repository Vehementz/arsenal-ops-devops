# Postfix

Postfix is a mail transfer agent (MTA) that routes and delivers email. These commands cover service management, configuration, queue handling, and troubleshooting.

#platform/linux #target/Mail #cat/DevOps

% postfix, mail, smtp, mta, postconf, mailq, postqueue

## Postfix - Check Service Status

Check whether the Postfix service is running.

```
systemctl status postfix
```

## Postfix - Start, Stop and Reload

Start, stop, or gracefully reload Postfix after a configuration change.

```
postfix start
postfix stop
postfix reload
```

## Postfix - Check Configuration

Check the configuration files for errors and problems.

```
postfix check
```

## Postfix - Show Non-Default Configuration

Display only the parameters that differ from Postfix defaults.

```
postconf -n
```

## Postfix - Show a Configuration Parameter

Display the current value of a single parameter.

```
postconf <parameter>
```

## Postfix - Set a Configuration Parameter

Set a parameter in `main.cf`, then reload Postfix to apply it.

```
postconf -e '<parameter>=<value>'
postfix reload
```

## Postfix - Show Master Process Configuration

Display the services defined in `master.cf`.

```
postconf -M
```

## Postfix - List the Mail Queue

Show every message currently in the queue.

```
postqueue -p
```

Equivalent shorthand:

```
mailq
```

## Postfix - Count Queued Messages

Count the messages waiting in the queue.

```
postqueue -j | wc -l
```

## Postfix - Flush the Mail Queue

Attempt immediate delivery of all queued mail.

```
postqueue -f
```

## Postfix - Flush Queue for a Domain

Attempt immediate delivery of queued mail for one destination domain.

```
postqueue -s <domain>
```

## Postfix - View a Queued Message

Display the content of a queued message by its queue ID.

```
postcat -q <queue_id>
```

## Postfix - Delete a Queued Message

Delete a single message from the queue by its queue ID.

```
postsuper -d <queue_id>
```

## Postfix - Delete All Queued Messages

Delete every message from the queue. This cannot be undone.

```
postsuper -d ALL
```

## Postfix - Delete Deferred Messages

Delete only the messages in the deferred queue.

```
postsuper -d ALL deferred
```

## Postfix - Requeue Messages

Return all queued messages to the incoming queue so they are re-processed.

```
postsuper -r ALL
```

## Postfix - Hold and Release a Message

Place a message on hold so it is not delivered, then release it later.

```
postsuper -h <queue_id>
postsuper -H <queue_id>
```

## Postfix - Follow the Mail Log

Follow Postfix log output in real time.

```
journalctl -u postfix -f
```

On systems that log to a file:

```
tail -f /var/log/mail.log
```

## Postfix - Search the Log for a Recipient

Find log lines for a given address.

```
grep '<email_address>' /var/log/mail.log
```

## Postfix - Find Rejected or Bounced Mail

Show deliveries that bounced or were deferred.

```
grep -E 'status=(bounced|deferred)' /var/log/mail.log
```

## Postfix - Send a Test Email

Send a test message from the command line.

```
echo "Test body" | mail -s "Test subject" <email_address>
```

## Postfix - Test an Address Lookup Table

Query a lookup table (for example virtual aliases) for a key.

```
postmap -q <key> hash:/etc/postfix/<table_file>
```

## Postfix - Rebuild a Lookup Table

Regenerate the indexed `.db` file after editing a hash table such as `virtual` or `transport`.

```
postmap /etc/postfix/<table_file>
```

## Postfix - Rebuild Aliases

Rebuild the aliases database after editing `/etc/aliases`.

```
newaliases
```

## Postfix - Test SMTP Connection with TLS

Test the SMTP service and its STARTTLS support on a host.

```
openssl s_client -starttls smtp -connect <host>:25
```
