# npm

npm is the default package manager for Node.js. It installs dependencies from the npm registry, runs project scripts, and publishes packages.

#platform/multiple #target/NodeJS #cat/PackageManagement

% npm, node, javascript, package management, scripts

## npm - Initialize a Project

Create a `package.json` interactively.

```
npm init
```

Accept every default instead of answering prompts:

```
npm init -y
```

## npm - Install All Dependencies

Install everything listed in `package.json`, updating `package-lock.json` if needed.

```
npm install
```

## npm - Install from the Lockfile

Install exactly what `package-lock.json` specifies, deleting `node_modules` first. This is the reproducible install to use in CI; it fails if the lockfile and `package.json` disagree.

```
npm ci
```

## npm - Add a Dependency

Install a package and save it to `dependencies`.

```
npm install express
```

Install a specific version:

```
npm install express@4.18.2
```

Install from a git repository:

```
npm install git+https://github.com/user/repo.git
```

## npm - Add a Development Dependency

Save the package to `devDependencies` so it is skipped by production installs.

```
npm install --save-dev jest
```

## npm - Install Production Dependencies Only

Skip `devDependencies` when building a runtime image.

```
npm install --omit=dev
```

## npm - Install a Global Package

Install a package system-wide so its binary is on `PATH`.

```
npm install -g typescript
```

List what is installed globally, without the dependency tree:

```
npm list -g --depth=0
```

## npm - Uninstall a Package

Remove a package and drop it from `package.json`.

```
npm uninstall express
```

## npm - Run a Script

Run a script defined in the `scripts` block of `package.json`.

```
npm run build
```

Pass arguments through to the underlying command:

```
npm run test -- --watch
```

List the scripts a project defines:

```
npm run
```

## npm - Run a Package Binary

Execute a package binary, downloading it temporarily if it is not installed.

```
npx create-react-app my-app
```

Run a binary from the local `node_modules`:

```
npm exec -- eslint .
```

## npm - Check for Outdated Packages

Show which dependencies have newer versions available.

```
npm outdated
```

Update packages within the ranges allowed by `package.json`:

```
npm update
```

## npm - Audit for Vulnerabilities

Report known vulnerabilities in the dependency tree.

```
npm audit
```

Apply the fixes that do not require a breaking change:

```
npm audit fix
```

Fail a CI build only on high severity findings:

```
npm audit --audit-level=high
```

## npm - Inspect the Dependency Tree

Show the installed tree, limited to top-level packages.

```
npm list --depth=0
```

Explain why a package is installed:

```
npm explain lodash
```

## npm - View Package Information

Show registry metadata for a package.

```
npm view express
```

Show just the published versions:

```
npm view express versions
```

## npm - Bump the Version

Increment the version in `package.json`, commit it, and create a git tag.

```
npm version patch
```

Use `minor` or `major` for larger bumps:

```
npm version minor
```

## npm - Publish a Package

Publish the current package to the registry.

```
npm publish
```

Publish a scoped package publicly:

```
npm publish --access public
```

Preview the exact file list that would be published:

```
npm pack --dry-run
```

## npm - Link a Local Package

Register the current package globally, then consume it from another project so local changes are picked up immediately.

```
npm link
```

In the consuming project:

```
npm link my-package
```

## npm - Work with Workspaces

Run an install for a single workspace in a monorepo.

```
npm install -w packages/api
```

Run a script in every workspace:

```
npm run build --workspaces
```

## npm - Manage Configuration

Show the resolved configuration.

```
npm config list
```

Set a value, such as a private registry:

```
npm config set registry https://registry.npmjs.org/
```

## npm - Clear the Cache

Force-clear the local package cache when installs behave inconsistently.

```
npm cache clean --force
```

Verify cache integrity instead of clearing it:

```
npm cache verify
```
