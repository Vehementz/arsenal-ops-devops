# kubectl

kubectl is the command-line client for the Kubernetes API. It creates, inspects, updates, and deletes cluster resources, and is the primary tool for debugging workloads running on a cluster.

#platform/multiple #target/Kubernetes #cat/DevOps

% kubectl, kubernetes, containers, orchestration, cluster

## kubectl - Show Cluster Information

Print the API server endpoint and the addresses of core services.

```
kubectl cluster-info
```

Show the client and server versions:

```
kubectl version
```

## kubectl - Manage Contexts

List every context in the kubeconfig, marking the current one.

```
kubectl config get-contexts
```

Switch to another cluster:

```
kubectl config use-context production
```

Print just the name of the active context:

```
kubectl config current-context
```

Set a default namespace so it can be omitted from later commands:

```
kubectl config set-context --current --namespace=staging
```

## kubectl - List Resources

List the pods in the current namespace.

```
kubectl get pods
```

Add the node and IP columns:

```
kubectl get pods -o wide
```

List across every namespace:

```
kubectl get pods -A
```

Watch for changes instead of returning immediately:

```
kubectl get pods -w
```

List several resource types at once:

```
kubectl get deployments,services,ingress
```

## kubectl - Filter Resources by Label

Select resources by label rather than by name.

```
kubectl get pods -l app=nginx
```

Combine selectors, and use set-based operators:

```
kubectl get pods -l 'env in (staging,prod),tier!=frontend'
```

Show the labels alongside the results:

```
kubectl get pods --show-labels
```

## kubectl - Sort and Filter the Output

Sort by a field, such as restart count or creation time.

```
kubectl get pods --sort-by=.status.containerStatuses[0].restartCount
```

Filter by a field selector, for example to find pods that are not running:

```
kubectl get pods --field-selector=status.phase!=Running
```

## kubectl - Describe a Resource

Print the full state of a resource together with its recent events. This is the first command to reach for when a pod will not start.

```
kubectl describe pod my-pod
```

Describe a node to see its capacity, conditions, and the pods assigned to it:

```
kubectl describe node worker-1
```

## kubectl - View Logs

Print the logs of a pod.

```
kubectl logs my-pod
```

Follow the log stream:

```
kubectl logs -f my-pod
```

Select a container in a multi-container pod:

```
kubectl logs my-pod -c sidecar
```

Read the logs of the previous container, which is how to see why a crash-looping pod died:

```
kubectl logs my-pod --previous
```

Limit the output by time or line count:

```
kubectl logs my-pod --since=1h --tail=100
```

Aggregate the logs of every pod behind a label:

```
kubectl logs -l app=nginx --all-containers --prefix
```

## kubectl - Run a Command in a Pod

Execute a command inside a running container.

```
kubectl exec my-pod -- ls /app
```

Open an interactive shell:

```
kubectl exec -it my-pod -- /bin/sh
```

Target a specific container:

```
kubectl exec -it my-pod -c sidecar -- /bin/bash
```

## kubectl - Apply a Manifest

Create or update resources from a file, recording the configuration so later applies can compute a diff.

```
kubectl apply -f deployment.yaml
```

Apply every manifest in a directory, recursively:

```
kubectl apply -R -f ./manifests
```

Apply a kustomization:

```
kubectl apply -k ./overlays/production
```

Apply from standard input:

```
cat deployment.yaml | kubectl apply -f -
```

## kubectl - Preview Changes Before Applying

Send the manifest to the API server for validation without persisting it.

```
kubectl apply -f deployment.yaml --dry-run=server
```

Show what would change against the live cluster state:

```
kubectl diff -f deployment.yaml
```

## kubectl - Generate a Manifest

Produce a manifest without creating anything, which is the quickest way to get a valid skeleton to edit.

```
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml
```

Generate a service definition the same way:

```
kubectl create service clusterip my-svc --tcp=80:8080 --dry-run=client -o yaml
```

## kubectl - Delete Resources

Delete the resources defined by a manifest.

```
kubectl delete -f deployment.yaml
```

Delete by name:

```
kubectl delete pod my-pod
```

Delete everything matching a label:

```
kubectl delete pods -l app=nginx
```

Force-delete a pod stuck in Terminating:

```
kubectl delete pod my-pod --grace-period=0 --force
```

## kubectl - Edit a Resource in Place

Open the live resource in an editor and apply the changes on save.

```
kubectl edit deployment my-app
```

## kubectl - Patch a Resource

Change a single field without opening an editor.

```
kubectl patch deployment my-app -p '{"spec":{"replicas":3}}'
```

Use a JSON patch for precise operations:

```
kubectl patch deployment my-app --type=json -p='[{"op":"replace","path":"/spec/replicas","value":5}]'
```

## kubectl - Scale a Deployment

Set the replica count directly.

```
kubectl scale deployment my-app --replicas=5
```

Scale only if the current count matches, avoiding a race with an autoscaler:

```
kubectl scale deployment my-app --current-replicas=3 --replicas=5
```

Create a horizontal autoscaler:

```
kubectl autoscale deployment my-app --min=2 --max=10 --cpu-percent=80
```

## kubectl - Manage a Rollout

Watch a rollout until it finishes or fails. This is the command to gate a deploy pipeline on.

```
kubectl rollout status deployment/my-app
```

Show the revision history:

```
kubectl rollout history deployment/my-app
```

Roll back to the previous revision:

```
kubectl rollout undo deployment/my-app
```

Roll back to a specific revision:

```
kubectl rollout undo deployment/my-app --to-revision=2
```

Restart every pod without changing the spec, which re-pulls images and re-reads mounted secrets:

```
kubectl rollout restart deployment/my-app
```

## kubectl - Wait for a Condition

Block until a resource reaches a condition, for use in scripts.

```
kubectl wait --for=condition=Ready pod -l app=nginx --timeout=120s
```

Wait for a resource to disappear:

```
kubectl wait --for=delete pod/my-pod --timeout=60s
```

## kubectl - Forward a Local Port

Tunnel a local port to a pod, so a cluster-internal service can be reached from the workstation.

```
kubectl port-forward pod/my-pod 8080:80
```

Forward to whichever pod backs a service:

```
kubectl port-forward service/my-svc 8080:80
```

## kubectl - Copy Files To and From a Pod

Copy a local file into a container.

```
kubectl cp ./config.yaml my-pod:/app/config.yaml
```

Copy a file out of a container:

```
kubectl cp my-pod:/var/log/app.log ./app.log
```

## kubectl - Expose a Workload as a Service

Create a service in front of an existing deployment.

```
kubectl expose deployment my-app --port=80 --target-port=8080
```

Create a NodePort service instead of the default ClusterIP:

```
kubectl expose deployment my-app --type=NodePort --port=80
```

## kubectl - Create ConfigMaps and Secrets

Create a ConfigMap from literal values.

```
kubectl create configmap app-config --from-literal=LOG_LEVEL=debug
```

Create one from a file or directory:

```
kubectl create configmap app-config --from-file=./config/
```

Create a generic secret:

```
kubectl create secret generic db-creds --from-literal=password=s3cret
```

Create a registry pull secret:

```
kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=ci --docker-password=token
```

## kubectl - Read a Secret Value

Secret values are base64-encoded in the API, so decode the field to read it.

```
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 -d
```

## kubectl - Manage Namespaces

List the namespaces in the cluster.

```
kubectl get namespaces
```

Create one:

```
kubectl create namespace staging
```

Run any command against a specific namespace:

```
kubectl get pods -n kube-system
```

## kubectl - Show Resource Usage

Show CPU and memory consumption per node. This requires the metrics-server to be installed.

```
kubectl top nodes
```

Show usage per pod, broken down by container:

```
kubectl top pods --containers
```

## kubectl - Inspect Events

List the events in a namespace, most recent last.

```
kubectl get events --sort-by=.metadata.creationTimestamp
```

Watch events as they arrive, filtered to warnings:

```
kubectl get events -w --field-selector type=Warning
```

## kubectl - Drain and Cordon Nodes

Mark a node unschedulable without moving anything off it.

```
kubectl cordon worker-1
```

Evict the pods so the node can be taken down for maintenance:

```
kubectl drain worker-1 --ignore-daemonsets --delete-emptydir-data
```

Return the node to service:

```
kubectl uncordon worker-1
```

## kubectl - Taint a Node

Add a taint so only pods with a matching toleration are scheduled there.

```
kubectl taint nodes worker-1 dedicated=gpu:NoSchedule
```

Remove the taint by repeating it with a trailing minus:

```
kubectl taint nodes worker-1 dedicated=gpu:NoSchedule-
```

## kubectl - Format the Output

Print the full resource as YAML, which is how to inspect defaulted and status fields.

```
kubectl get pod my-pod -o yaml
```

Extract a single field with JSONPath:

```
kubectl get pod my-pod -o jsonpath='{.status.podIP}'
```

Build a table from arbitrary fields:

```
kubectl get pods -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,STATUS:.status.phase'
```

List the images running in the cluster:

```
kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' | sort -u
```

## kubectl - Look Up the API Schema

List every resource type the cluster serves, with its short name and API group.

```
kubectl api-resources
```

Describe the fields of a resource, which avoids guessing at manifest structure:

```
kubectl explain deployment.spec.strategy
```

Show the full field tree:

```
kubectl explain pod --recursive
```

## kubectl - Debug a Pod

Attach an ephemeral debug container to a running pod, useful when the image has no shell.

```
kubectl debug -it my-pod --image=busybox --target=my-container
```

Create a copy of a pod with a debug container instead of modifying the original:

```
kubectl debug my-pod -it --image=busybox --copy-to=my-pod-debug
```

Start a throwaway pod for network testing:

```
kubectl run tmp-shell --rm -it --image=nicolaka/netshoot -- /bin/bash
```

## kubectl - Check Permissions

Ask whether the current credentials allow an action.

```
kubectl auth can-i create deployments
```

Check as another user or service account:

```
kubectl auth can-i list secrets --as=system:serviceaccount:default:my-sa
```

List everything the current user may do in a namespace:

```
kubectl auth can-i --list -n default
```

## kubectl - Annotate and Label Resources

Add a label to an existing resource.

```
kubectl label pod my-pod env=production
```

Overwrite a label that is already set:

```
kubectl label pod my-pod env=staging --overwrite
```

Remove a label with a trailing minus:

```
kubectl label pod my-pod env-
```

Add an annotation:

```
kubectl annotate deployment my-app description='payments API'
```

## kubectl - Proxy to the API Server

Open an authenticated local proxy to the API, so it can be queried with an ordinary HTTP client.

```
kubectl proxy --port=8001
```

Then query a resource directly:

```
curl http://localhost:8001/api/v1/namespaces/default/pods
```
