# Docker Swarm

Docker Swarm is Docker's built-in container orchestrator. It groups Docker hosts into a cluster of manager and worker nodes and runs replicated services and stacks across them.

#platform/multiple #target/Containers #cat/Orchestration

% docker, swarm, cluster, orchestration, service, stack, node, secret

## Docker Swarm - Initialize Swarm

Turn the current host into a swarm manager.

```
docker swarm init --advertise-addr <manager-ip>
```

## Docker Swarm - Show Join Token

Print the command for adding a worker or a manager to the swarm.

```
docker swarm join-token worker
docker swarm join-token manager
```

### Docker Swarm - Rotate Join Token

Invalidate the current join token and generate a new one.

```
docker swarm join-token --rotate worker
```

## Docker Swarm - Join Swarm

Join the current host to a swarm with a join token.

```
docker swarm join --token <token> <manager-ip>:2377
```

## Docker Swarm - Leave Swarm

Remove the current node from the swarm (`--force` is required on the last manager).

```
docker swarm leave
docker swarm leave --force
```

## Docker Swarm - Show Swarm State

Show whether the node is in a swarm, its role and the cluster ID.

```
docker info --format '{{.Swarm.LocalNodeState}} {{.Swarm.ControlAvailable}} {{.Swarm.Cluster.ID}}'
```

## Docker Swarm - Update Swarm Settings

Change cluster-wide settings, such as how long task history is kept.

```
docker swarm update --task-history-limit <n>
```

## Docker Swarm - Enable Autolock

Encrypt the managers' Raft keys so a restarted manager needs an unlock key.

```
docker swarm update --autolock=true
```

### Docker Swarm - Unlock Manager

Unlock a restarted manager when autolock is enabled.

```
docker swarm unlock
```

### Docker Swarm - Show Unlock Key

Print the current unlock key.

```
docker swarm unlock-key
```

## Docker Swarm - List Nodes

List the nodes in the swarm with their role, status and availability.

```
docker node ls
```

## Docker Swarm - Inspect Node

Show the details of a node in readable form.

```
docker node inspect --pretty <node>
```

## Docker Swarm - List Node Tasks

List the tasks running on a node (the current node by default).

```
docker node ps <node>
```

## Docker Swarm - Promote Node

Make a worker node a manager.

```
docker node promote <node>
```

### Docker Swarm - Demote Node

Make a manager node a worker.

```
docker node demote <node>
```

## Docker Swarm - Drain Node

Move all tasks off a node, for example before maintenance.

```
docker node update --availability drain <node>
```

### Docker Swarm - Reactivate Node

Allow a drained node to receive tasks again.

```
docker node update --availability active <node>
```

## Docker Swarm - Add Node Label

Add a label to a node, for use in placement constraints.

```
docker node update --label-add <key>=<value> <node>
```

## Docker Swarm - Remove Node

Remove a node that has left the swarm or is down.

```
docker node rm <node>
docker node rm --force <node>
```

## Docker Swarm - Create Service

Create a replicated service that publishes a port.

```
docker service create --name <service> --replicas <n> --publish <published-port>:<container-port> <image>
```

### Docker Swarm - Create Global Service

Run one task of a service on every node.

```
docker service create --name <service> --mode global <image>
```

### Docker Swarm - Create Service With Constraint

Place a service's tasks only on nodes that match a constraint.

```
docker service create --name <service> --constraint node.role==worker --constraint node.labels.<key>==<value> <image>
```

### Docker Swarm - Create Service With Secret

Create a service that can read a swarm secret at `/run/secrets/<secret>`.

```
docker service create --name <service> --secret <secret> <image>
```

## Docker Swarm - List Services

List the services in the swarm with their replica counts.

```
docker service ls
```

## Docker Swarm - List Service Tasks

List a service's tasks and the nodes they run on.

```
docker service ps <service>
```

### Docker Swarm - Show Full Task Errors

List a service's tasks without truncating error messages.

```
docker service ps --no-trunc <service>
```

## Docker Swarm - Inspect Service

Show a service's configuration in readable form.

```
docker service inspect --pretty <service>
```

## Docker Swarm - Show Service Logs

Follow the logs of every task of a service.

```
docker service logs -f <service>
```

## Docker Swarm - Scale Service

Change the number of replicas of one or more services.

```
docker service scale <service>=<n>
```

## Docker Swarm - Update Service Image

Roll out a new image to a service, a set number of tasks at a time.

```
docker service update --image <image>:<tag> --update-parallelism 1 --update-delay 10s <service>
```

### Docker Swarm - Force Service Redeploy

Restart all the tasks of a service without changing its configuration.

```
docker service update --force <service>
```

### Docker Swarm - Update Service Ports

Publish a new port on a service, or stop publishing one.

```
docker service update --publish-add <published-port>:<container-port> <service>
docker service update --publish-rm <published-port> <service>
```

## Docker Swarm - Roll Back Service

Revert a service to its previous configuration.

```
docker service rollback <service>
```

## Docker Swarm - Remove Service

Remove one or more services.

```
docker service rm <service>
```

## Docker Swarm - Deploy Stack

Deploy or update a stack from a Compose file.

```
docker stack deploy -c <docker-compose.yml> <stack>
```

### Docker Swarm - Deploy Stack With Registry Auth

Deploy a stack that uses images from a private registry.

```
docker stack deploy --with-registry-auth -c <docker-compose.yml> <stack>
```

## Docker Swarm - List Stacks

List the stacks in the swarm.

```
docker stack ls
```

## Docker Swarm - List Stack Services

List the services of a stack.

```
docker stack services <stack>
```

## Docker Swarm - List Stack Tasks

List the tasks of a stack.

```
docker stack ps <stack>
```

## Docker Swarm - Remove Stack

Remove a stack and its services.

```
docker stack rm <stack>
```

## Docker Swarm - Create Secret

Create a secret from a file, or from standard input with `-`.

```
docker secret create <secret> <file>
printf '<value>' | docker secret create <secret> -
```

## Docker Swarm - List Secrets

List the secrets in the swarm.

```
docker secret ls
```

## Docker Swarm - Remove Secret

Remove a secret that no service is using.

```
docker secret rm <secret>
```

## Docker Swarm - Create Config

Create a config, a non-secret file made available to services.

```
docker config create <config> <file>
```

### Docker Swarm - List Configs

List the configs in the swarm.

```
docker config ls
```

## Docker Swarm - Create Overlay Network

Create a network that services on different nodes can share.

```
docker network create --driver overlay --attachable <network>
```

### Docker Swarm - Create Encrypted Overlay Network

Create an overlay network that encrypts traffic between nodes.

```
docker network create --driver overlay --opt encrypted <network>
```
