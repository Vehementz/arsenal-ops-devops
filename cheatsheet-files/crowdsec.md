Certainly! Here's a structured and concise guide for using CrowdSec commands, formatted in a similar style to the Helm documentation you provided:

# CrowdSec

CrowdSec is an open-source and collaborative security automation engine designed to protect servers, services, containers, or virtual machines exposed on the internet with a server-side agent. It analyzes visitor behavior and provides an adapted response to all kinds of attacks.

#platform/multiple #target/servers, containers, VMs #cat/Security

% crowdsec, security, intrusion prevention, automation

## CrowdSec - View Metrics

Display metrics about CrowdSec's activities such as events processed, alerts sent, etc.

```
docker exec crowdsec cscli metrics
```

## CrowdSec - List Bans

List currently enforced bans.

```
docker exec crowdsec cscli decisions list
```

## CrowdSec - Install Collections

Manually install specific collections of CrowdSec configurations.

```
docker exec crowdsec cscli collections install crowdsecurity/traefik
```

## CrowdSec - Update Hub

Update the CrowdSec configurations hub to the latest versions available.

```
docker exec crowdsec cscli hub update
```

## CrowdSec - Upgrade Hub

Upgrade the installed items from the CrowdSec hub.

```
docker exec crowdsec cscli hub upgrade
```

## CrowdSec - Add Bouncer

Register a new bouncer to the system. Save the API key as required.

```
docker exec crowdsec cscli bouncers add bouncer-traefik
```

## CrowdSec - Ban IP Address

Manually ban an IP address.

```
docker exec crowdsec cscli decisions add --ip 192.168.0.101
```

## CrowdSec - Unban IP Address

Remove a ban from an IP address.

```
docker exec crowdsec cscli decisions delete --ip 192.168.0.101
```

