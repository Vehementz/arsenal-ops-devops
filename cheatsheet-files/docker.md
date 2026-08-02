# docker

docker is the command-line client for the Docker Engine daemon. It builds images, runs and inspects containers, and manages the networks, volumes and disk space that containerised workloads consume on a host.

#platform/multiple #target/Containers #cat/DevOps

% docker, containers, images, registry, volumes, networks, build, runtime

## docker - Check the Client and Daemon

Confirm which client is talking to which daemon before anything else. The client and server versions are independent, and on a server you have just been handed they are frequently not the same.

```
docker version
```

Print only the two versions, which is enough for a compatibility check in a script:

```
docker version --format '{{.Client.Version}} {{.Server.Version}}'
```

Show daemon-wide state: storage driver, cgroup version, logging driver, container and image counts.

```
docker info
```

Pull a single field out, for example the directory the daemon actually stores everything under:

```
docker info --format '{{.DockerRootDir}}'
```

## docker - Run a Container

Run a container in the foreground. Without `-d` the container's stdout is attached to your terminal and Ctrl-C stops it, which is what you want when trying an image out.

```
docker run nginx:1.27
```

Run detached with a stable name. Always name long-lived containers: the generated names change on every recreate, so scripts and runbooks that reference them break.

```
docker run -d --name web nginx:1.27
```

Run a throwaway container that deletes itself and its anonymous volumes on exit. Use this for one-shot tools so stopped containers do not accumulate on the host.

```
docker run --rm -it alpine:3.20 sh
```

Override the working directory and the user the process runs as. Running as a non-root UID is the single cheapest hardening step on an on-premise host, because a container escape then starts from an unprivileged account.

```
docker run --rm -w /srv -u 1000:1000 alpine:3.20 id
```

Override the image's entrypoint when you need a shell in an image that normally starts a daemon:

```
docker run --rm -it --entrypoint sh nginx:1.27
```

Attach the container to a specific user-defined network so it can resolve its peers by name:

```
docker run -d --name api --network backend myapp:1.4
```

## docker - Publish Ports to the Host

Map a host port to a container port. Without a publish flag the container port is reachable only from the container's own network, not from the host or the LAN.

```
docker run -d --name web -p 8080:80 nginx:1.27
```

Bind to a single host interface instead of every interface. On an on-premise box with a public NIC, `-p 8080:80` exposes the service to the whole network; binding to loopback keeps it behind a reverse proxy.

```
docker run -d --name web -p 127.0.0.1:8080:80 nginx:1.27
```

Publish a UDP port, and publish every port the image declares with `EXPOSE` to random high ports:

```
docker run -d --name dns -p 5353:53/udp coredns/coredns
```

```
docker run -d --name web -P nginx:1.27
```

Ask a running container which host ports it ended up on, which is the only reliable way to read the mapping after `-P`:

```
docker port web
```

```
docker port web 80/tcp
```

## docker - Pass Environment Variables

Set variables individually. A bare `-e NAME` with no value forwards the value from your current shell.

```
docker run -d --name api -e LOG_LEVEL=debug -e DATABASE_URL=postgres://db/app myapp:1.4
```

Load them from a file instead. This keeps secrets out of the process list and out of shell history, unlike `-e`, which any user on the host can read via `ps` or `docker inspect`.

```
docker run -d --name api --env-file ./api.env myapp:1.4
```

Read back the environment the daemon actually gave the container:

```
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' api
```

## docker - Mount Data Into a Container

Bind mount a host directory. The container sees the host path directly, so ownership and SELinux labels are the host's, and anything the container writes survives independently of Docker. Use bind mounts for configuration and for code you are actively editing.

```
docker run -d --name web -v /srv/www:/usr/share/nginx/html nginx:1.27
```

Mount it read-only so a compromised container cannot rewrite host configuration:

```
docker run -d --name web -v /srv/nginx.conf:/etc/nginx/nginx.conf:ro nginx:1.27
```

Use a named volume instead when the data belongs to the container rather than the host. Docker creates the volume on first use and manages its lifetime; this is the right choice for databases.

```
docker run -d --name db -v pgdata:/var/lib/postgresql/data postgres:16
```

The difference is in the first argument: a path starting with `/` is a bind mount, anything else is a volume name. Confirm which one a container actually got:

```
docker inspect -f '{{range .Mounts}}{{.Type}} {{.Source}} -> {{.Destination}}{{println}}{{end}}' db
```

Mount a tmpfs for scratch data that must never touch disk:

```
docker run -d --name api --tmpfs /tmp:rw,size=64m myapp:1.4
```

## docker - Limit CPU and Memory

Cap memory and CPU. Without limits one container can exhaust the host and take every other service down with it, so on a shared on-premise server these are not optional.

```
docker run -d --name api --memory 512m --cpus 1.5 myapp:1.4
```

`--memory` is a hard limit: exceeding it gets the process OOM-killed by the kernel, and the container exits with code 137. `--memory-reservation` is a soft limit that only applies under host memory pressure.

```
docker run -d --name api --memory 512m --memory-reservation 256m myapp:1.4
```

Pin a container to specific cores, which matters for latency-sensitive workloads sharing a host:

```
docker run -d --name api --cpuset-cpus 2,3 myapp:1.4
```

Change limits on a container that is already running, without recreating it:

```
docker update --memory 1g --cpus 2 api
```

## docker - Set Restart Policies and Health Checks

Set a restart policy so the container comes back after a crash and after a host reboot. `unless-stopped` restarts the container in both cases except when you stopped it deliberately, which is usually what you want for a service; `always` restarts it even after a manual stop, once the daemon restarts.

```
docker run -d --name api --restart unless-stopped myapp:1.4
```

Retry a limited number of times instead, so a container that is broken rather than flaky stops burning CPU:

```
docker run -d --name api --restart on-failure:5 myapp:1.4
```

Read the policy back, and change it on a running container:

```
docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' api
```

```
docker update --restart unless-stopped api
```

Add a health check at run time when the image does not define one. The daemon runs the command inside the container and marks it healthy or unhealthy; a restart policy alone cannot detect a process that is alive but wedged.

```
docker run -d --name api --health-cmd 'curl -fsS http://localhost:8080/healthz || exit 1' --health-interval 30s --health-timeout 5s --health-retries 3 --health-start-period 20s myapp:1.4
```

Read the current health state and the last few probe results:

```
docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' api
```

Disable a health check baked into the image when it is wrong for your deployment:

```
docker run -d --name api --no-healthcheck myapp:1.4
```

## docker - List Containers

List the running containers.

```
docker ps
```

Include stopped ones. This is where you find the container that exited two minutes ago and the exit code that explains why.

```
docker ps -a
```

Show the writable-layer size of each container, which is how you spot a container logging into its own filesystem:

```
docker ps -as
```

Show only IDs, for piping into another command, and stop truncating long values:

```
docker ps -aq
```

```
docker ps --no-trunc
```

Show just the most recently created container, regardless of state:

```
docker ps -l
```

## docker - Filter and Format Listings

Filter server-side rather than grepping, so the match is on the real field and not on whatever the column happens to show.

```
docker ps -a --filter status=exited
```

```
docker ps -a --filter name=airflow
```

Find every container started from a given image, which is how you work out what still depends on an image you want to delete:

```
docker ps -a --filter ancestor=myapp:1.4
```

Filter by exit code or by label:

```
docker ps -a --filter exited=137
```

```
docker ps -a --filter label=com.example.stack=payments
```

Build a custom table. `table` gives you headers; omit it and you get bare lines suited to scripting.

```
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

```
docker ps -a --format '{{.Names}}'
```

Emit one JSON object per container for machine consumption:

```
docker ps -a --format json
```

The same filter and format flags work on `docker images`, `docker network ls` and `docker volume ls`:

```
docker images --filter reference='myapp*' --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'
```

## docker - Read Container Logs

Print everything the container has written to stdout and stderr. With the default json-file driver the daemon stores this on disk, so it survives a container restart but not a `docker rm`.

```
docker logs api
```

Follow the stream, showing only the recent tail so you are not scrolled off by a week of history:

```
docker logs -f --tail 100 api
```

Restrict by time. Both `--since` and `--until` take an absolute timestamp or a relative offset, which makes it easy to cut the window around an incident.

```
docker logs --since 30m api
```

```
docker logs --since 2026-08-02T09:00:00Z --until 2026-08-02T09:15:00Z api
```

Prefix each line with a timestamp, useful when the application does not log one itself:

```
docker logs -ft api
```

Find the log file on disk, for example to check how large it has grown when no rotation is configured:

```
docker inspect -f '{{.LogPath}}' api
```

## docker - Run a Command Inside a Running Container

Open an interactive shell in a running container. `-i` keeps stdin open and `-t` allocates a TTY; you need both for a usable shell.

```
docker exec -it api sh
```

Run a single command and return, which is the form to use in scripts:

```
docker exec api cat /etc/nginx/nginx.conf
```

Enter as root to install a debugging tool in a container that normally runs unprivileged:

```
docker exec -it -u 0 api sh
```

Run from a specific directory, with extra environment:

```
docker exec -it -w /srv -e LOG_LEVEL=trace api sh
```

`docker attach` is not the same thing. It connects your terminal to the container's existing PID 1 rather than starting a new process, so what you type goes to that process and Ctrl-C may kill the container. Reach for it only when you actually need the main process's console.

```
docker attach api
```

Attach without forwarding stdin or signals, which makes it a safe read-only tail of the main process:

```
docker attach --no-stdin --sig-proxy=false api
```

Detach from an attached container without stopping it using the escape sequence Ctrl-P Ctrl-Q, or override it:

```
docker attach --detach-keys 'ctrl-e,e' api
```

## docker - Inspect an Object With Go Templates

Dump the full low-level record of any object: container, image, network or volume.

```
docker inspect api
```

Extract a single field instead of piping the whole document through jq. `-f` takes a Go template, and this is the fastest way to get one value in a script.

```
docker inspect -f '{{.State.Status}} {{.State.ExitCode}}' api
```

Range over a map to get the container's address on each network it is attached to:

```
docker inspect -f '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}={{$conf.IPAddress}} {{end}}' api
```

Print a subtree as JSON when the structure is easier to read than to template:

```
docker inspect -f '{{json .NetworkSettings.Ports}}' api
```

Force the object type when a container and an image share a name:

```
docker inspect --type image myapp:1.4
```

Include the writable layer size of a container:

```
docker inspect -s -f '{{.SizeRw}}' api
```

## docker - Watch Resource Usage and Processes

Stream live CPU, memory, network and block I/O per container. This is the first place to look when the host load is up and you do not know which container is responsible.

```
docker stats
```

Take a single sample instead of streaming, so it can be used in a script or a cron check:

```
docker stats --no-stream
```

Include stopped containers, and format the output as a table of just what you need:

```
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
```

List the processes running inside a container, as seen from the host. Any `ps` options you append are passed through, so this works even when the image has no `ps` binary of its own.

```
docker top api
```

```
docker top api aux
```

## docker - Copy Files In and Out

Copy a file out of a container, for example a crash dump or a generated config.

```
docker cp api:/var/log/app.log ./app.log
```

Copy a file in. This works on stopped containers too, which is how you fix a bad config file in a container that will not start.

```
docker cp ./nginx.conf web:/etc/nginx/nginx.conf
```

Preserve UID and GID so the copied files are not silently reowned:

```
docker cp -a ./site web:/usr/share/nginx/html
```

Stream a directory out as a tar archive without landing it on disk first:

```
docker cp api:/srv/data - | gzip > data.tar.gz
```

## docker - Stop, Kill and Restart Containers

Stop a container gracefully. The daemon sends SIGTERM, waits, and only then sends SIGKILL, so the process gets a chance to flush and close connections.

```
docker stop api
```

Shorten or lengthen that grace period. The default is 10 seconds, which is far too short for a database that has to checkpoint.

```
docker stop -t 60 db
```

`docker kill` skips the grace period entirely and sends SIGKILL immediately. Use it only when a container is ignoring SIGTERM, and expect unflushed data to be lost.

```
docker kill api
```

Send an arbitrary signal instead, for example to make a process reload its configuration in place:

```
docker kill -s HUP web
```

Start a stopped container again, keeping its configuration, volumes and name:

```
docker start api
```

Restart in one step, with the same grace-period semantics as `stop`:

```
docker restart -t 30 api
```

Block until a container exits and print its exit code, which is how you gate a script on a one-shot job:

```
docker wait migrate
```

## docker - Remove Containers

Remove a stopped container. It must be stopped first; this is deliberate, so a running service cannot be deleted by a stray command.

```
docker rm api
```

Force removal of a running container. This is a SIGKILL followed by a delete, with no graceful shutdown.

```
docker rm -f api
```

Also delete the container's anonymous volumes. Named volumes are never removed by `docker rm`, so a database's data survives.

```
docker rm -v api
```

Clear out every exited container in one go:

```
docker rm $(docker ps -aq --filter status=exited)
```

Rename a container rather than recreating it, when the generated name is unhelpful:

```
docker rename nervous_hopper api
```

## docker - List and Pull Images

List local images. Sizes shown are per image, and layers shared between images are counted more than once, so the column does not sum to disk usage.

```
docker images
```

Show digests, which is what you compare when you need to know whether two hosts really run the same bits:

```
docker images --digests
```

Show dangling images, the untagged leftovers a rebuild orphans:

```
docker images --filter dangling=true
```

Pull an image from a registry. Pin a tag, or better, pin a digest: tags are mutable and can point at different content tomorrow.

```
docker pull nginx:1.27
```

```
docker pull nginx@sha256:0f1a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4c5d6e7f8
```

Pull a specific architecture on a multi-arch host:

```
docker pull --platform linux/amd64 nginx:1.27
```

Scanning images for vulnerabilities is a separate job; see the trivy and grype cheatsheets.

## docker - Tag and Push Images

Add a name to an existing image. A tag is only a pointer, so this costs nothing and does not copy layers.

```
docker tag myapp:1.4 registry.example.com/team/myapp:1.4
```

Push it to a private registry. The registry host is taken from the image name, which is why the tag must be fully qualified before pushing.

```
docker push registry.example.com/team/myapp:1.4
```

Push every tag of a repository at once:

```
docker push -a registry.example.com/team/myapp
```

## docker - Move Images Without a Registry

Save an image, with all its layers and tags, to a tar archive. On an air-gapped on-premise network this is how images get in without a registry.

```
docker save -o myapp-1.4.tar myapp:1.4
```

Save several images into one archive, compressing on the way out:

```
docker save myapp:1.4 nginx:1.27 | gzip > bundle.tar.gz
```

Load them on the target host. `load` restores images with their original names and tags, unlike `import`, which takes a flat filesystem tarball and gives you a single-layer image with no metadata.

```
docker load -i myapp-1.4.tar
```

```
gunzip -c bundle.tar.gz | docker load
```

Restrict the transfer to one architecture when the image is multi-platform:

```
docker save --platform linux/amd64 -o myapp-amd64.tar myapp:1.4
```

## docker - Inspect and Remove Images

Show the layers of an image, newest first, with the instruction that created each one. This is how you find the layer responsible for an image being far larger than expected.

```
docker history myapp:1.4
```

Show the full commands instead of the truncated ones, as a table of just size and instruction:

```
docker history --no-trunc --format 'table {{.Size}}\t{{.CreatedBy}}' myapp:1.4
```

Read the image's own metadata, for example the architecture it was built for:

```
docker image inspect -f '{{.Architecture}}/{{.Os}}' myapp:1.4
```

Remove an image. This fails while any container, including a stopped one, still references it, which is a feature rather than an obstacle.

```
docker rmi myapp:1.3
```

Remove a tag while keeping the underlying image, by deleting only one of several names pointing at it:

```
docker rmi registry.example.com/team/myapp:1.3
```

Delete only the dangling images, which is the safe subset to reclaim without thinking:

```
docker image prune
```

## docker - Build an Image

Build from the Dockerfile in the current directory and tag the result. The final argument is the build context: every file under it is sent to the builder, so build from the narrowest directory that works and keep a `.dockerignore`.

```
docker build -t myapp:1.4 .
```

Point at a Dockerfile outside the context, which is how one context serves several images:

```
docker build -f docker/Dockerfile.prod -t myapp:1.4 .
```

Pass build-time variables. These are not secrets: they are recorded in the image history and readable by anyone who can pull the image.

```
docker build --build-arg VERSION=1.4 --build-arg GOPROXY=http://proxy.internal -t myapp:1.4 .
```

Mount a real secret for a single instruction instead, so it never lands in a layer:

```
docker build --secret id=npmrc,src=$HOME/.npmrc -t myapp:1.4 .
```

Stop at a named stage of a multi-stage Dockerfile. Building the `builder` or `test` stage gives you the intermediate image with the toolchain still in it, which is how you debug a build that fails only in CI.

```
docker build --target builder -t myapp:builder .
```

Ignore the layer cache when a cached `RUN apt-get update` is serving you stale package indexes:

```
docker build --no-cache -t myapp:1.4 .
```

Modern Docker routes `docker build` through BuildKit, which builds stages in parallel and hides output it considers uninteresting. Force the full log when a build fails and the error is scrolled away:

```
docker build --progress=plain -t myapp:1.4 .
```

Build for another architecture, and push the result straight to a registry rather than loading it locally:

```
docker build --platform linux/arm64 -t myapp:1.4 .
```

```
docker build --platform linux/amd64,linux/arm64 -t registry.example.com/team/myapp:1.4 --push .
```

Check the Dockerfile for problems without running the build:

```
docker build --check .
```

## docker - Manage Networks

List the networks the daemon knows about. `bridge`, `host` and `none` are built in and cannot be removed.

```
docker network ls
```

Create a user-defined bridge network. Containers on one of these get DNS resolution by container name, which containers on the default `bridge` network do not; this is the reason to create one rather than relying on the default.

```
docker network create backend
```

Pin the subnet, which matters on-premise when the default 172.17.0.0/16 range collides with your corporate network:

```
docker network create --subnet 10.42.0.0/24 --gateway 10.42.0.1 backend
```

Create a network with no route off the host, for a database that must never be reachable externally:

```
docker network create --internal db-internal
```

Attach and detach a running container:

```
docker network connect backend api
```

```
docker network disconnect backend api
```

Give a container an extra DNS name on the network:

```
docker network connect --alias postgres backend db
```

See which containers are attached to a network and what addresses they hold:

```
docker network inspect -f '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}' backend
```

```
docker network inspect -f '{{range .IPAM.Config}}{{.Subnet}} {{.Gateway}}{{end}}' bridge
```

`--network host` skips network namespacing entirely: the container shares the host's stack, `-p` becomes meaningless, and any port the process binds is bound on the host. It removes NAT overhead but also removes the isolation, so use it deliberately.

```
docker run -d --name exporter --network host prom/node-exporter
```

## docker - Manage Volumes

List volumes. Compose-created ones are named after the project; the long hexadecimal names are anonymous volumes left behind by containers that mounted a path the image declared as a volume.

```
docker volume ls
```

Create one explicitly, so its name and labels are yours rather than generated:

```
docker volume create pgdata
```

Find out where the data actually lives on the host. Local volumes sit under the daemon's root directory, typically `/var/lib/docker/volumes/<name>/_data`, and can be backed up with ordinary filesystem tools while the container is stopped.

```
docker volume inspect -f '{{.Name}} {{.Mountpoint}}' pgdata
```

Back an NFS share with a volume, which is common on-premise when the data must not live on a single node's disk:

```
docker volume create --driver local --opt type=nfs --opt o=addr=10.0.0.5,rw --opt device=:/exports/pgdata pgdata
```

List the volumes no container references:

```
docker volume ls --filter dangling=true
```

Remove one. This refuses while a container still uses it, including a stopped container, so delete the container first.

```
docker volume rm pgdata
```

## docker - Check Disk Usage and Reclaim Space

Show what Docker is consuming, split into images, containers, volumes and build cache, with how much of each is reclaimable. On an on-premise host this is usually the answer to a full `/var`.

```
docker system df
```

Break it down per object, so you can see which specific image or volume is the problem:

```
docker system df -v
```

Remove stopped containers, unused networks, dangling images and dangling build cache. It prompts before acting; read the list it prints.

```
docker system prune
```

`-a` additionally removes every image not used by a running container, and `--volumes` removes anonymous volumes. Both are destructive in ways that are easy to underestimate: `-a` will delete images you cannot re-pull on an air-gapped host, and `--volumes` will delete data that no container currently references, including the volumes of a stack you merely stopped. Do not run this pair on a production host without checking `docker system df -v` first.

```
docker system prune -a --volumes
```

Target one category instead, which is almost always the better move:

```
docker container prune
```

```
docker image prune -a --filter 'until=720h'
```

```
docker builder prune --filter 'until=168h'
```

## docker - Authenticate to a Private Registry

Log in to a registry. Passing the credential on stdin keeps it out of your shell history and out of the host's process list.

```
echo "$REGISTRY_TOKEN" | docker login registry.example.com -u ci --password-stdin
```

Credentials are written to `~/.docker/config.json`, base64-encoded and not encrypted unless a credential helper is configured. On a shared server, treat that file as a secret.

```
docker login registry.example.com
```

Drop the stored credential for one registry:

```
docker logout registry.example.com
```

## docker - Point the CLI at a Remote Daemon

List the configured contexts. A context binds a name to a daemon endpoint, so one workstation can drive several on-premise hosts without editing environment variables.

```
docker context ls
```

Create a context that reaches a remote daemon over SSH. This needs nothing on the far side except a working SSH login and a user in the `docker` group, which makes it the simplest safe option.

```
docker context create prod01 --docker host=ssh://ops@prod01.example.com
```

Create one for a TLS-protected TCP endpoint:

```
docker context create prod02 --docker "host=tcp://prod02.example.com:2376,ca=~/.docker/ca.pem,cert=~/.docker/cert.pem,key=~/.docker/key.pem"
```

Switch the default, and check which one is active:

```
docker context use prod01
```

```
docker context show
```

Run a single command against another context without switching, which is the safer habit when several hosts are in play:

```
docker --context prod01 ps
```

Read a context's endpoint, and export it to hand to a colleague:

```
docker context inspect -f '{{.Name}} {{.Endpoints.docker.Host}}' prod01
```

```
docker context export prod01 prod01.dockercontext
```

## docker - Stream Daemon Events

Follow the daemon's event stream in real time. This shows starts, stops, OOM kills, health status changes and image pulls as they happen, and it is the fastest way to catch a container that restarts too quickly to appear in `docker ps`.

```
docker events
```

Replay a past window instead of waiting for new events:

```
docker events --since 1h --until 10m
```

Narrow to the events that matter, for example only containers dying:

```
docker events --filter type=container --filter event=die
```

Watch one container, or everything carrying a label:

```
docker events --filter container=api
```

```
docker events --filter label=com.example.stack=payments
```

Emit JSON for a log shipper:

```
docker events --format json
```

## docker - Inspect and Snapshot a Container Filesystem

List every file that has been added, changed or deleted in the container's writable layer since it started. `A` is added, `C` changed, `D` deleted. This tells you what a container has been writing outside its volumes, which is where surprise disk usage and lost-on-restart state come from.

```
docker diff api
```

Turn the current state of a container into a new image. Useful for capturing a broken container for offline analysis before deleting it, or for snapshotting a manually fixed appliance.

```
docker commit -m 'state at incident 2026-08-02' api forensics/api:incident-4471
```

Committed images are not reproducible: nothing records how the container got that way. Rebuild from a Dockerfile for anything you intend to ship, and keep `commit` for forensics.

```
docker commit -c 'CMD ["/bin/sh"]' api scratchpad/api:debug
```

Combine the two with `save` to get a snapshot off the host entirely:

```
docker commit api forensics/api:incident-4471 && docker save -o incident-4471.tar forensics/api:incident-4471
```
