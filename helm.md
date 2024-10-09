Here's a similar structured and concise guide for `helm`, mimicking the style you've outlined for Ansible:

# Helm

Helm is the package manager for Kubernetes. It allows developers and operators to package, configure, and deploy applications and services onto Kubernetes clusters.

#platform/multiple #target/Kubernetes #cat/DevOps

% helm, kubernetes, package management, deployment

## Helm - Create a Chart

Create a new chart directory structure with the specified `name`.

```
helm create <name>
```

## Helm - Package a Chart

Package a chart directory into a versioned chart archive file.

```
helm package <chart-path>
```

## Helm - Lint a Chart

Validate that the chart follows best practices and is correctly formatted.

```
helm lint <chart>
```

## Helm - Show All Information of a Chart

Display detailed information about a chart including its dependencies, values, and templates.

```
helm show all <chart>
```

## Helm - Show Values of a Chart

Show the default configuration values of a chart.

```
helm show values <chart>
```

## Helm - Download a Chart

Download a chart from a repository to your local machine.

```
helm pull <chart>
```

## Helm - Download and Unpack a Chart

Download a chart and immediately unpack it into a directory.

```
helm pull <chart> --untar
```

## Helm - Verify a Chart

Download and verify the chart before unpacking it.

```
helm pull <chart> --verify
```

## Helm - Download a Specific Version of a Chart

Specify a version number to download a specific version of a chart.

```
helm pull <chart> --version <version>
```

## Helm - List Dependencies of a Chart

List all dependencies required by the chart.

```
helm dependency list <chart>
```

## Helm - Install a Chart

Install a chart with a specific `name` into the Kubernetes cluster.

```
helm install <name> <chart>
```

## Helm - Install a Chart in a Namespace

Install a chart into a specific namespace within the Kubernetes cluster.

```
helm install <name> <chart> --namespace <namespace>
```

## Helm - Install a Chart with Custom Values

Override default configuration values using inline arguments or a custom YAML file.

```
helm install <name> <chart> --set key1=val1,key2=val2
helm install <name> <chart> --values <yaml-file/url>
```

## Helm - Dry Run an Installation

Simulate an installation to validate the chart and view the computed outputs.

```
helm install <name> <chart> --dry-run --debug
```

## Helm - Uninstall a Chart

Remove a deployed chart from the Kubernetes cluster by release `name`.

```
helm uninstall <name>
```

## Helm - Upgrade a Release

```
helm upgrade <release> <chart>
```

## Helm - Upgrade a Release Atomically

```
helm upgrade <release> <chart> --atomic
```

## Helm - Update Dependencies During Upgrade

```
helm upgrade <release> <chart> --dependency-update
```

## Helm - Upgrade to a Specific Version of a Chart

```
helm upgrade <release> <chart> --version <version_number>
```

## Helm - Specify Values During Upgrade

```
helm upgrade <release> <chart> --values <yaml-file/url>
```

## Helm - Set Values Directly on Command Line During Upgrade

```
helm upgrade <release> <chart> --set key1=val1,key2=val2
```

## Helm - Force Resources Update During Upgrade

```
helm upgrade <release> <chart> --force
```

## Helm - Roll Back a Release

```
helm rollback <release> <revision>
```

## Helm - Clean Up Failed Rollback Resources

```
helm rollback <release> <revision> --cleanup-on-fail
```

## Helm - Add a Chart Repository

```
helm repo add <repo-name> <url>
```

## Helm - List Chart Repositories

```
helm repo list
```

## Helm - Update Chart Repositories

```
helm repo update
```

## Helm - Remove a Chart Repository

```
helm repo remove <repo_name>
```

## Helm - Generate an Index File

```
helm repo index <DIR>
```

## Helm - Merge Generated Index with Existing Index

```
helm repo index <DIR> --merge <existing_index.yaml>
```

## Helm - Search Chart Repositories by Keyword

```
helm search repo <keyword>
```

## Helm - Search Helm Hub for Charts

```
helm search hub <keyword>
```

## Helm - List All Deployed Releases

```
helm list
```

## Helm - List Releases Across All Namespaces

```
helm list --all-namespaces
```

## Helm - List Releases by Label Selector

```
helm list -l key1=value1,key2=value2
```

## Helm - Show the Status of a Named Release

```
helm status <release>
```

## Helm - Show Historical Revisions for a Release

```
helm history <release>
```

## Helm - Get Detailed Information About a Release

```
helm get all <release>
```

## Helm - Download Hooks of a Release

```
helm get hooks <release>
```

## Helm - Download Manifest of a Release

```
helm get manifest <release>
```

## Helm - Show Notes of a Release

```
helm get notes <release>
```

## Helm - Download Values of a Release

```
helm get values <release>
```

## Helm - Install a Plugin from a URL or Path

```
helm plugin install <path/url1>
```

## Helm - List Installed Plugins

```
helm plugin list
```

## Helm - Update an Installed Plugin

```
helm plugin update <plugin>
```

## Helm - Uninstall a Plugin

```
helm plugin uninstall <plugin>
```



