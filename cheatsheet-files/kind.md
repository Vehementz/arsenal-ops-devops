# kind

kind runs local Kubernetes clusters using Docker containers as nodes. It is designed for testing Kubernetes itself and for CI, and it gives a throwaway cluster in about a minute.

#platform/multiple #target/Kubernetes #cat/DevOps

% kind, kubernetes, local cluster, docker, testing

## kind - Create a Cluster

Create a single-node cluster named `kind` and point the current kubeconfig context at it.

```
kind create cluster
```

Give the cluster a name so several can coexist:

```
kind create cluster --name dev
```

Fail fast rather than hanging if the cluster does not come up:

```
kind create cluster --wait 60s
```

## kind - Create a Cluster on a Specific Kubernetes Version

Pin the node image to choose the Kubernetes version. Use the digest published with the kind release that you are running, since node images are tied to a kind version.

```
kind create cluster --image kindest/node:v1.31.0
```

## kind - Create a Multi-Node Cluster

Describe the nodes in a config file.

```
cat <<EOF > kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
EOF
```

Then create the cluster from it:

```
kind create cluster --name multi --config kind-config.yaml
```

## kind - Expose Ports to the Host

Map container ports to the host so an ingress controller is reachable from the workstation. The `ingress-ready` label is what the common ingress-nginx kind manifest selects on.

```
cat <<EOF > kind-ingress.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF
```

Create the cluster with that config:

```
kind create cluster --config kind-ingress.yaml
```

## kind - Mount a Host Directory

Bind a directory on the host into a node, so a hostPath volume can reach local files.

```
cat <<EOF > kind-mount.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraMounts:
  - hostPath: /home/user/data
    containerPath: /data
EOF
```

## kind - List Clusters

Show the clusters kind is managing.

```
kind get clusters
```

List the container nodes backing a cluster:

```
kind get nodes --name dev
```

## kind - Load a Local Image

Push an image from the local Docker daemon into the cluster nodes, so a pod can use it without a registry. This is the main reason to reach for kind during development.

```
kind load docker-image my-app:dev --name dev
```

Load several images at once:

```
kind load docker-image my-app:dev my-worker:dev --name dev
```

Load from a saved tar archive instead:

```
kind load image-archive my-app.tar --name dev
```

Because the image is already present, set `imagePullPolicy: IfNotPresent` in the manifest so Kubernetes does not try to fetch it from a registry.

## kind - Manage the Kubeconfig

Print the kubeconfig for a cluster.

```
kind get kubeconfig --name dev
```

Write it into the default kubeconfig and switch to it:

```
kind export kubeconfig --name dev
```

Write it to a separate file instead of touching the main one:

```
kind get kubeconfig --name dev > ./dev.kubeconfig
```

## kind - Export Cluster Logs

Dump the logs of every node into a directory, which is what to collect when a CI run fails.

```
kind export logs ./kind-logs --name dev
```

## kind - Delete a Cluster

Delete a cluster and remove its context from the kubeconfig.

```
kind delete cluster --name dev
```

Delete every cluster kind is managing:

```
kind delete clusters --all
```

## kind - Build a Node Image

Build a node image from a local Kubernetes source tree, for testing an unreleased Kubernetes build.

```
kind build node-image /path/to/kubernetes
```

Tag the result and use it:

```
kind build node-image /path/to/kubernetes --image kindest/node:custom
```

## kind - Show the Version

Print the kind version along with the Go runtime and platform.

```
kind version
```
