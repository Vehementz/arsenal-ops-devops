Here’s a structured and concise guide for **Trivy**, mimicking the style used for Helm, Molecule, and Checkov:

# Trivy

Trivy is a comprehensive security scanner that detects vulnerabilities, misconfigurations, and secrets in containers, filesystems, and Kubernetes clusters.

#platform/multiple #target/Security #cat/DevOps

% trivy, security scanning, vulnerabilities, container images, sbom

## Trivy - Scan a Docker Image

Scan a Docker image for vulnerabilities from Docker Hub.

```
trivy image python
```

For images hosted on other registries:

```
trivy image cgr.dev/chainguard/nginx:latest
```

## Trivy - Scan a Filesystem

Recursively scan local directories for vulnerabilities, misconfigurations, and exposed secrets.

```
trivy fs <path>
```

For example, scan a Python project folder:

```
mkdir python-project && cd python-project
python -m venv venv
./venv/bin/pip install WTForms==2.3.3 Werkzeug==2.0.1
./venv/bin/pip freeze > requirements.txt
trivy fs .
```

Or scan a Node.js project:

```
mkdir node_project && cd node_project
npm init -y
npm install qs@6.5.2
trivy fs .
```

## Trivy - Scan a Kubernetes Cluster

Scan an entire Kubernetes cluster for security vulnerabilities and misconfigurations.

```
trivy k8s --report summary <cluster-name>
```

For example, to scan a local Kubernetes cluster created with Kind:

```
kind create cluster --name test-cluster
trivy k8s --report summary test-cluster
```

## Trivy - Generate and Scan an SBOM

Generate a Software Bill of Materials (SBOM) in CycloneDX format from a container image:

```
trivy image -f cyclonedx -o results.cdx.json nginx
```

Scan the generated SBOM for vulnerabilities:

```
trivy sbom results.cdx.json
```

To enable license scanning along with vulnerabilities, use the `--scanners` option:

```
trivy sbom --scanners license results.cdx.json
```
