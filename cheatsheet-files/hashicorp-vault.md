# HashiCorp Vault

HashiCorp Vault is a secrets management tool that stores, generates and controls access to tokens, passwords, certificates and encryption keys through an API, CLI and UI. The `vault` CLI talks to a Vault server set in `VAULT_ADDR`.

#platform/multiple #target/Secrets #cat/Security

% vault, hashicorp, secrets, kv, token, policy, pki, transit

## HashiCorp Vault - Set Server Address

Point the CLI at a Vault server.

```
export VAULT_ADDR=https://<vault-host>:8200
```

## HashiCorp Vault - Start Dev Server

Start an in-memory, already-unsealed dev server (for testing only, never production).

```
vault server -dev -dev-root-token-id=<root-token>
```

## HashiCorp Vault - Start Server

Start a Vault server from a configuration file.

```
vault server -config=<config.hcl>
```

## HashiCorp Vault - Show Status

Show seal status, version and HA mode of the server.

```
vault status
```

## HashiCorp Vault - Initialize

Initialize a new server and print the unseal keys and root token.

```
vault operator init -key-shares=5 -key-threshold=3
```

## HashiCorp Vault - Unseal

Provide one unseal key share (repeat until the threshold is reached).

```
vault operator unseal
```

## HashiCorp Vault - Seal

Seal the server so it stops serving requests.

```
vault operator seal
```

## HashiCorp Vault - Login With Token

Authenticate the CLI with a token.

```
vault login <token>
```

### HashiCorp Vault - Login With Userpass

Authenticate with the userpass auth method.

```
vault login -method=userpass username=<user>
```

### HashiCorp Vault - Login With OIDC

Authenticate through an OIDC provider (opens a browser).

```
vault login -method=oidc role=<role>
```

## HashiCorp Vault - Enable KV Engine

Enable a KV version 2 secrets engine at a path.

```
vault secrets enable -path=<mount> kv-v2
```

## HashiCorp Vault - List Secrets Engines

List the enabled secrets engines and their paths.

```
vault secrets list -detailed
```

## HashiCorp Vault - Write Secret

Create or update a secret in a KV store.

```
vault kv put -mount=<mount> <path> <key>=<value>
```

### HashiCorp Vault - Patch Secret

Update some keys of a secret without overwriting the others.

```
vault kv patch -mount=<mount> <path> <key>=<value>
```

## HashiCorp Vault - Read Secret

Read a secret from a KV store.

```
vault kv get -mount=<mount> <path>
```

### HashiCorp Vault - Read Single Field

Print only one field of a secret (useful in scripts).

```
vault kv get -mount=<mount> -field=<key> <path>
```

### HashiCorp Vault - Read Secret As JSON

Print a secret as JSON.

```
vault kv get -mount=<mount> -format=json <path>
```

### HashiCorp Vault - Read Secret Version

Read a specific version of a secret.

```
vault kv get -mount=<mount> -version=<n> <path>
```

## HashiCorp Vault - List Secrets

List the secret keys under a path.

```
vault kv list -mount=<mount> <path>
```

## HashiCorp Vault - Delete Secret

Soft-delete the latest version of a secret (can be undeleted).

```
vault kv delete -mount=<mount> <path>
```

### HashiCorp Vault - Undelete Secret

Restore soft-deleted versions of a secret.

```
vault kv undelete -mount=<mount> -versions=<n> <path>
```

### HashiCorp Vault - Destroy Secret Version

Permanently destroy versions of a secret.

```
vault kv destroy -mount=<mount> -versions=<n> <path>
```

### HashiCorp Vault - Delete All Versions

Permanently delete a secret, all its versions and its metadata.

```
vault kv metadata delete -mount=<mount> <path>
```

## HashiCorp Vault - Rollback Secret

Restore an earlier version of a secret as the new latest version.

```
vault kv rollback -mount=<mount> -version=<n> <path>
```

## HashiCorp Vault - Enable Auth Method

Enable an auth method (e.g. userpass, approle, oidc).

```
vault auth enable <method>
```

## HashiCorp Vault - List Auth Methods

List the enabled auth methods.

```
vault auth list
```

## HashiCorp Vault - Create Userpass User

Create a user for the userpass auth method with policies attached.

```
vault write auth/userpass/users/<user> password=<password> policies=<policy>
```

## HashiCorp Vault - Create AppRole

Create an AppRole for machine authentication.

```
vault write auth/approle/role/<role> token_policies=<policy> token_ttl=1h token_max_ttl=4h
```

### HashiCorp Vault - Get AppRole Role ID

Read the role ID of an AppRole.

```
vault read auth/approle/role/<role>/role-id
```

### HashiCorp Vault - Generate AppRole Secret ID

Generate a new secret ID for an AppRole.

```
vault write -f auth/approle/role/<role>/secret-id
```

### HashiCorp Vault - Login With AppRole

Exchange a role ID and secret ID for a token.

```
vault write auth/approle/login role_id=<role-id> secret_id=<secret-id>
```

## HashiCorp Vault - Write Policy

Upload a policy from an HCL file.

```
vault policy write <policy> <policy.hcl>
```

## HashiCorp Vault - List Policies

List installed policies.

```
vault policy list
```

## HashiCorp Vault - Read Policy

Print the contents of a policy.

```
vault policy read <policy>
```

## HashiCorp Vault - Create Token

Create a token with policies and a TTL.

```
vault token create -policy=<policy> -ttl=1h
```

## HashiCorp Vault - Lookup Token

Show information about the current token (or a given one).

```
vault token lookup <token>
```

## HashiCorp Vault - Check Token Capabilities

Show what the current token can do on a path.

```
vault token capabilities <path>
```

## HashiCorp Vault - Renew Token

Renew the current token's lease.

```
vault token renew
```

## HashiCorp Vault - Revoke Token

Revoke a token and all its children.

```
vault token revoke <token>
```

## HashiCorp Vault - Revoke Leases

Revoke every lease under a prefix (e.g. all dynamic credentials of an engine).

```
vault lease revoke -prefix <path>
```

## HashiCorp Vault - Encrypt With Transit

Encrypt data with a Transit key (plaintext must be base64-encoded).

```
vault write transit/encrypt/<key> plaintext=$(echo -n "<data>" | base64)
```

### HashiCorp Vault - Decrypt With Transit

Decrypt Transit ciphertext and decode it.

```
vault write -field=plaintext transit/decrypt/<key> ciphertext=<ciphertext> | base64 -d
```

## HashiCorp Vault - Issue PKI Certificate

Issue a certificate from a PKI role.

```
vault write pki/issue/<role> common_name=<host.example.com> ttl=24h
```

## HashiCorp Vault - Enable Audit Log

Enable a file audit device.

```
vault audit enable file file_path=/var/log/vault_audit.log
```

## HashiCorp Vault - Take Raft Snapshot

Save a snapshot of integrated (Raft) storage for backup.

```
vault operator raft snapshot save <backup.snap>
```

### HashiCorp Vault - Restore Raft Snapshot

Restore integrated storage from a snapshot.

```
vault operator raft snapshot restore <backup.snap>
```

## HashiCorp Vault - List Raft Peers

List the nodes in the Raft cluster.

```
vault operator raft list-peers
```

## HashiCorp Vault - Show Path Help

Show the API help for any path.

```
vault path-help <path>
```

## HashiCorp Vault - Print Curl Equivalent

Print the equivalent curl command instead of running a CLI command.

```
vault kv get -output-curl-string -mount=<mount> <path>
```
