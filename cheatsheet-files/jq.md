# jq

jq is a filter language for JSON. It reads one or more JSON documents, applies a program to them, and writes JSON or raw text out, which makes it the tool for turning `kubectl -o json`, `docker inspect`, and REST API responses into something a shell script or a human can act on.

#platform/multiple #target/JSON #cat/TextProcessing

% jq, json, filtering, kubectl, docker, rest api, parsing, pipelines

## jq - Pretty-Print and Validate JSON

`.` is the identity filter: it returns the input unchanged, and jq re-emits it indented and syntax-highlighted. This is the fastest way to make an API response readable.

```
jq . response.json
```

Change the indent width, or use tabs, when the output is going into a file that has a house style:

```
jq --indent 4 . response.json
```

```
jq --tab . response.json
```

Sort object keys so two dumps of the same resource can be diffed without spurious key-order noise:

```
jq -S . response.json
```

`empty` produces no output, so it turns jq into a pure validator: exit status 0 means the document parsed, 5 means it did not.

```
jq empty response.json && echo VALID
```

## jq - Select Keys and Nested Paths

Chain field names with dots to walk into an object. A missing key yields `null` rather than an error, which is why a typo in a path silently returns nothing.

```
jq '.meta.region' response.json
```

Use bracket syntax when a key contains a dot, a dash, or any character that would break the dot form. Kubernetes annotations and Docker Compose labels almost always need this.

```
jq '.Config.Labels["com.docker.compose.project"]' container.json
```

Indexing into a `null` is fine, but indexing into the wrong *type* is an error. Add `?` to make the step give up quietly instead:

```
jq '.missing?.deep' response.json
```

## jq - Index and Slice Arrays

Arrays are indexed from 0, and negative indices count back from the end.

```
jq '.items[0]' response.json
```

```
jq -c '.items[-1]' response.json
```

Slices take a half-open range, so `[1:3]` returns elements 1 and 2. Omit either bound to run to the start or the end.

```
jq -c '.items[1:3]' response.json
```

```
jq -c '.items[:2] | map(.name)' response.json
```

The same syntax slices strings, which is handy for truncating long IDs and digests:

```
jq -r '.meta.request_id[0:3]' response.json
```

## jq - Iterate with the Array Iterator

`.[]` emits each element of an array (or each value of an object) as a separate result, so the rest of the pipeline runs once per element. This is the core idiom for processing lists.

```
jq -r '.items[].name' response.json
```

Pipe into further filters to reach inside each element:

```
jq -r '.items[] | .owner.email' response.json
```

Iterators nest, flattening as they go:

```
jq -r '.items[].tags[]' response.json
```

Wrap the whole expression in `[ ]` to collect the stream back into a single array, which you need whenever a later filter expects an array rather than a stream:

```
jq -c '[.items[] | .name]' response.json
```

## jq - Filter with select

`select(condition)` passes its input through when the condition is true and emits nothing when it is false. Combined with `.[]` this is the JSON equivalent of `grep`.

```
jq -c '.items[] | select(.state == "running")' response.json
```

Numeric and boolean comparisons work directly, and conditions combine with `and`, `or`, `not`:

```
jq -r '.items[] | select(.state != "running" and .cpu == 0) | .name' response.json
```

Test array membership with `index`, which returns the position or `null`:

```
jq -r '.items[] | select(.tags | index("web")) | .name' response.json
```

Match strings with `test` (regex), `startswith`, `endswith`, or `contains`:

```
jq -r '.items[] | select(.name | test("^[ab]")) | .name' response.json
```

`IN` reads better than a chain of `or` when checking against a fixed set:

```
jq -r '.items[] | select(.state | IN("failed","stopped")) | .name' response.json
```

## jq - Map Over an Array

`map(f)` applies `f` to every element and returns an array. Unlike `.[]` it keeps the array structure, so it composes with `length`, `add`, and `sort_by`.

```
jq -c '.items | map(.name)' response.json
```

`map(select(...))` filters in place and is the usual way to count matches:

```
jq -c '.items | map(select(.state == "running")) | length' response.json
```

Project each element down to the fields you care about, dropping the rest:

```
jq -c '.items | map({id, name})' response.json
```

## jq - Test for Keys with has and in

`has` asks whether a key or index exists. This is not the same as checking for a non-null value, which matters when an API distinguishes "absent" from "explicitly null".

```
jq '.meta | has("region")' response.json
```

On an array, `has` takes an index:

```
jq '.items[0].tags | has(1)' response.json
```

`in` is `has` with the arguments swapped, so the key flows in from the pipeline:

```
jq -r '.items[] | select(.owner.team | in({"core":1,"platform":1})) | .name' response.json
```

## jq - Convert Objects to Entries and Back

`to_entries` turns an object into an array of `{key, value}` pairs, which is how you iterate over a map whose keys you do not know in advance — labels, annotations, and Docker network names all look like this.

```
jq -c '.meta | to_entries' response.json
```

```
jq -r '.meta | to_entries[] | "\(.key): \(.value|type)"' response.json
```

`from_entries` reverses it, so the pair is the standard way to filter or rewrite an object's keys:

```
jq -c '.meta | to_entries | map(select(.value | type == "string")) | from_entries' response.json
```

`with_entries(f)` is shorthand for `to_entries | map(f) | from_entries`:

```
jq -c '.meta | with_entries(select(.key | startswith("r")))' response.json
```

```
jq -c '.meta | with_entries(.key |= ascii_upcase)' response.json
```

## jq - Build New Objects

`{a: .b}` constructs a fresh object, which is how you reshape a verbose API payload into exactly the fields a downstream tool needs.

```
jq -c '.items[] | {name: .name, team: .owner.team}' response.json
```

`{name, cpu}` is shorthand for `{name: .name, cpu: .cpu}`:

```
jq -c '.items[] | {name, cpu}' response.json
```

Parenthesise an expression to use it as a key, which builds a lookup map keyed on data:

```
jq -c '.items[] | {(.name): .cpu}' response.json
```

Values can be any expression, but must be parenthesised if they contain a pipe:

```
jq -c '{host: .meta.region, count: (.items | length)}' response.json
```

Building `{key, value}` pairs and feeding `from_entries` gives a name-to-value index in one pass:

```
jq -c '.items | map({key: .name, value: .cpu}) | from_entries' response.json
```

## jq - Interpolate Values into Strings

`\(...)` embeds a jq expression inside a string literal. Non-string values are stringified automatically, so you do not need `tostring`.

```
jq -r '.items[] | "\(.name) runs on team \(.owner.team) using \(.cpu)m"' response.json
```

Interpolation happily contains its own pipeline:

```
jq -r '.items[] | "\(.name)=\(.tags | join(","))"' response.json
```

```
jq -r '"total=\(.total) pages=\((.total / 25) | ceil)"' response.json
```

## jq - Control the Output Encoding

By default jq emits JSON, so a string comes out with quotes around it. `-r` writes strings raw, and it is mandatory whenever the output feeds another shell command — otherwise the quotes become part of the argument.

```
jq -r '.meta.region' response.json
```

`-j` is `-r` without the trailing newline, for assembling a line yourself:

```
jq -j '.items[] | .name, " "' response.json
```

`-c` prints each result on one line. This is what turns jq into a line-oriented stream that `while read`, `xargs`, or a log shipper can consume:

```
jq -c '.items[]' response.json
```

```
jq -c '.items[] | {name, state}' response.json | while read -r line; do echo "got: $line"; done
```

## jq - Inject Shell Values with --arg and --argjson

Never interpolate a shell variable into the filter text: a value containing a quote or a `$` will corrupt the program. `--arg` binds it as a jq variable, always as a string, correctly escaped.

```
jq -r --arg team "$TEAM" '.items[] | select(.owner.team == $team) | .name' response.json
```

`--argjson` parses the value as JSON instead, which is what you want for numbers, booleans, arrays, and objects — `--arg` would make `200` the string `"200"` and every numeric comparison would fail.

```
jq -r --argjson min "$MIN" '.items[] | select(.cpu >= $min) | .name' response.json
```

Combine with `-n` to build a JSON request body from shell values, safely:

```
jq -n --arg name web --argjson replicas 3 '{name: $name, replicas: $replicas}'
```

Feed a whole captured document in as a variable:

```
jq -n --argjson pods "$(kubectl get pods -o json)" '$pods.items | length'
```

Every named argument is also collected in `$ARGS.named`, and `--args` puts trailing words into `$ARGS.positional`:

```
jq -rn --args '$ARGS.positional[]' web api cache
```

## jq - Read Environment Variables

`env.NAME` reads a single variable and `$ENV` is the whole environment as an object. This avoids a `--arg` for values that are already exported.

```
jq -rn 'env.KUBECONFIG'
```

```
jq -rn '$ENV.HOME'
```

Mix environment data into output the same as any other value:

```
jq -r '.items[] | select(.owner.team=="core") | "\(env.REGION)/\(.name)"' response.json
```

## jq - Handle Multiple Documents

`-s` (slurp) reads the entire input into a single array before running the filter. This is how you aggregate over a stream of newline-delimited JSON, such as `docker ps --format json`.

```
docker ps --format json | jq -s 'length'
```

```
docker ps --format json | jq -sr 'group_by(.State)[] | "\(.[0].State): \(length)"'
```

`-n` starts with `null` as the input, and `inputs` then pulls the documents in explicitly. This streams rather than buffering, so it scales to large files where `-s` would not.

```
docker ps --format json | jq -rn '[inputs | .Names] | join(",")'
```

```
docker ps --format json | jq -n 'reduce inputs as $c (0; . + 1)'
```

`input` reads exactly one more document, and `inputs` spans several files, which lets you compare two dumps in one invocation:

```
jq -n '[inputs] | length' before.json after.json
```

## jq - Inspect Shape with length, keys and type

`length` is polymorphic: element count for arrays, key count for objects, character count for strings, absolute value for numbers, and 0 for `null`.

```
jq '.items | length' response.json
```

```
jq '.meta.request_id | length' response.json
```

`keys` lists an object's keys sorted; `keys_unsorted` preserves document order, which is what you want when you are about to build a table header.

```
jq -c '.items[0] | keys' response.json
```

```
jq -c '.items[0] | keys_unsorted' response.json
```

`type` returns the type name as a string, and is how you defend a filter against a field that is sometimes a string and sometimes an array.

```
jq -r '.meta | to_entries[] | "\(.key): \(.value|type)"' response.json
```

## jq - Aggregate, Sort and Group

`add` sums an array of numbers, and also concatenates an array of arrays or strings.

```
jq '[.items[].cpu] | add' response.json
```

```
jq -c '[.items[].tags] | add' response.json
```

`min` and `max` work on the array itself; `min_by`/`max_by` take an expression, which is what you need on arrays of objects.

```
jq -c '[.items[].cpu] | min, max' response.json
```

```
jq -r '.items | max_by(.cpu) | .name' response.json
```

`sort_by` accepts several keys for a compound sort, and negating a numeric key reverses it:

```
jq -c '.items | sort_by(-.cpu) | map(.name)' response.json
```

```
jq -c '.items | sort_by(.owner.team, .name) | map(.name)' response.json
```

`group_by` returns an array of arrays sharing a key, which is the basis of any per-group tally:

```
jq -c '.items | group_by(.owner.team) | map({team: .[0].owner.team, total: (map(.cpu)|add)})' response.json
```

`unique` deduplicates and sorts; `unique_by` keeps the first element of each group:

```
jq -c '[.items[].tags[]] | unique' response.json
```

```
jq -c '.items | unique_by(.owner.team) | map(.name)' response.json
```

## jq - Find Paths in Unfamiliar JSON

`paths` emits every path in the document as an array of keys and indices. Filtering it with `paths(scalars)` gives just the leaves, which is the fastest way to discover where a value actually lives in a Kubernetes object you have never inspected before.

```
jq -r 'paths(scalars) | join(".")' response.json
```

Restrict it to a subtree to keep the output manageable:

```
jq -c '.meta | paths' response.json
```

`getpath` reads a path given as data rather than as syntax, so the path can come from a variable or from `paths` itself:

```
jq -c 'getpath(["items",0,"owner","team"])' response.json
```

Like `.a.b`, it returns `null` for a path that does not exist instead of failing:

```
jq -c 'getpath(["nope","deep"])' response.json
```

Note that `leaf_paths` was removed in jq 1.7; use `paths(scalars)` instead.

## jq - Supply Defaults with the Alternative Operator

`a // b` evaluates to `b` when `a` produces `null`, `false`, or nothing at all. Use it on every optional field so one absent key does not put `null` in the middle of a report.

```
jq -r '.meta.zone // "unknown"' response.json
```

```
jq -r '.items[] | .tags[0] // "untagged"' response.json
```

It is what makes a `@tsv` table readable when the source data is sparse:

```
jq -r '.items[] | [.name, (.owner.slack // "-")] | @tsv' response.json
```

Pairing it with `empty` drops the element entirely rather than substituting a placeholder:

```
jq -c '[.items[] | .name // empty]' response.json
```

## jq - Suppress and Catch Errors

A type error aborts the whole run, which in a pipeline over heterogeneous documents means one odd record kills the report. `?` suppresses the error for that filter and produces nothing.

```
jq -r '.items[] | .tags | .foo?' response.json
```

`try f catch g` is the explicit form and lets you emit something in the error case, with the message available as `.`:

```
jq -r 'try (.items[0].tags | tonumber) catch "not a number"' response.json
```

```
jq -r '.items[] | try (.cpu / 0) catch "div-by-zero"' response.json
```

`error` raises an error yourself, which combined with `-e` is how a validation filter fails a pipeline deliberately:

```
jq -r '.items[] | try error("boom-\(.name)") catch .' response.json
```

## jq - Format for Other Tools

`@csv` and `@tsv` take an array and emit a properly quoted row, which is what to use instead of hand-building a line with interpolation and hoping no field contains a comma.

```
jq -r '.items[] | [.id, .name, .state, .cpu] | @csv' response.json
```

```
jq -r '.items[] | [.name, .owner.team] | @tsv' response.json
```

`@sh` quotes a value for safe reuse in a shell command, which matters the moment a container or pod name contains something unexpected:

```
jq -r '.items[] | @sh "docker rm \(.name)"' response.json
```

`@base64` and `@base64d` encode and decode, the everyday need being Kubernetes secrets:

```
jq -r '.data | to_entries[] | "\(.key)=\(.value | @base64d)"' secret.json
```

```
jq -r '.meta.request_id | @base64' response.json
```

`@uri` percent-encodes a query parameter, and `@json` serialises a value back into a JSON string:

```
jq -rn '"a b&c" | @uri'
```

```
jq -r '.items[0] | @json' response.json
```

## jq - Convert Types and Case

`tostring` renders any value as a string, which is required before `@tsv` on a mixed row or before string functions like `split`.

```
jq -r '.total | tostring | length' response.json
```

`tonumber` parses a numeric string, the usual case being an API that returns counts as strings:

```
jq -rn '"42" | tonumber + 1'
```

`ascii_downcase` and `ascii_upcase` normalise case before comparing, which is safer than assuming an API is consistent:

```
jq -r '.items[] | .state | ascii_downcase' response.json
```

`ltrimstr` and `rtrimstr` strip a fixed prefix or suffix and leave the value untouched if it does not match, which makes them safe to apply blindly to a list of image names:

```
jq -rn '"registry.example.com/web:1.4.2" | ltrimstr("registry.example.com/")'
```

`split` and `capture` handle the rest of the string work:

```
jq -rn '"registry.example.com/web:1.4.2" | split(":") | .[-1]'
```

```
jq -rn '"registry.example.com/web:1.4.2" | capture("(?<repo>[^:]+):(?<tag>.+)") | .tag'
```

`tojson` and `fromjson` cross the boundary between a value and its JSON text, needed for fields that hold embedded JSON such as `kubectl.kubernetes.io/last-applied-configuration`:

```
jq -r '.metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"] | fromjson | .spec.replicas' deploy.json
```

## jq - Delete and Merge Fields

`del` removes keys or array elements. Dropping the bulky part of a document is the quickest way to make `kubectl get -o json` readable.

```
jq -c 'del(.items)' response.json
```

```
jq -c '.items[0] | del(.owner, .tags)' response.json
```

`pick` is the inverse and keeps only the listed paths:

```
jq -c '.items[0] | pick(.name, .owner.team)' response.json
```

`+` merges two objects shallowly, with the right-hand side winning on conflicts. It replaces nested objects wholesale rather than merging into them.

```
jq -c '.meta + {region: "us-east", zone: "a"}' response.json
```

`*` merges recursively, so nested objects are combined key by key. This is the operator for overlaying a patch onto a manifest.

```
jq -cn '{a:{b:1,c:2}} * {a:{c:9,d:3}}'
```

On arrays `+` concatenates:

```
jq -c '.items[0].tags + ["extra"]' response.json
```

## jq - Accumulate with reduce and foreach

`reduce f as $x (init; update)` folds a stream down to a single value. It expresses tallies that `group_by` cannot, because the accumulator can be any shape.

```
jq -c 'reduce .items[] as $i ({}; .[$i.owner.team] += $i.cpu)' response.json
```

```
jq -c 'reduce .items[] as $i ({}; .[$i.name] = $i.cpu)' response.json
```

`foreach` has the same shape plus an extract expression, and emits a result at every step instead of only at the end — use it for running totals and cumulative reports.

```
jq -c '[foreach .items[] as $i (0; . + $i.cpu; {name: $i.name, running_total: .})]' response.json
```

`limit` stops a stream early, which avoids walking a huge document when you only want a sample:

```
jq -c '[limit(2; .items[].name)]' response.json
```

## jq - Drive Shell Logic with the Exit Status

By default jq exits 0 whenever the program ran, even if the result was `false` or `null`. `-e` makes the exit status reflect the *output*: 0 for a truthy last result, 1 for `false` or `null`, and 4 when nothing was produced at all.

```
jq -e '.status == "ok"' response.json
```

That makes jq usable directly as a shell condition, with the output discarded:

```
if jq -e '.items | any(.state == "failed")' response.json >/dev/null; then echo "failed items present"; fi
```

Exit 4 on empty output is the one to rely on for "did any record match", since `select` emits nothing rather than `false`:

```
jq -e '.items[] | select(.state == "pending")' response.json; echo "exit=$?"
```

A malformed document exits 5 regardless of `-e`, so a parse failure and a false result stay distinguishable.

```
jq -e . response.json >/dev/null || echo "invalid or falsy"
```

## jq - Report on Kubernetes Pods

Flattening `kubectl get -o json` into a TSV table gives you columns that `-o custom-columns` cannot express, such as values from two different subtrees.

```
kubectl get pods -o json | jq -r '.items[] | [.metadata.name, .status.phase, .spec.nodeName] | @tsv'
```

Find pods that are not healthy. Binding the pod name to `$p` before descending into the container list is the key trick: once you pipe into `.status.containerStatuses[]` the pod-level fields are out of scope.

```
kubectl get pods -o json | jq -r '.items[] | .metadata.name as $p | .status.containerStatuses[] | select(.restartCount > 3) | "\($p)/\(.name) restarts=\(.restartCount)"'
```

List pods where any container is not ready, which catches workloads that are `Running` but broken:

```
kubectl get pods -o json | jq -r '.items[] | select([.status.containerStatuses[].ready] | all | not) | .metadata.name'
```

Count pods per node to spot a scheduling imbalance:

```
kubectl get pods -A -o json | jq -r '.items | group_by(.spec.nodeName)[] | "\(.[0].spec.nodeName): \(length) pods"'
```

## jq - Audit Images and Resource Requests

Inventory every image running in the cluster. `unique` both sorts and deduplicates, so this is a one-line answer to "what are we actually running".

```
kubectl get pods -A -o json | jq -r '[.items[].spec.containers[].image] | unique | .[]'
```

Flag the mutable tags, which is the usual first finding of an on-premise cluster audit:

```
kubectl get pods -A -o json | jq -r '[.items[].spec.containers[].image] | map(select(endswith(":latest"))) | .[]'
```

Find containers with no CPU request, since those land in the BestEffort class and are evicted first under node pressure:

```
kubectl get pods -A -o json | jq -r '.items[] | .metadata.name as $p | .spec.containers[] | select(.resources.requests.cpu == null) | "\($p)/\(.name) has no cpu request"'
```

Build a full requests-and-limits table, using `//` so containers with nothing set still get a row:

```
kubectl get pods -A -o json | jq -r '.items[] | .metadata.name as $p | .spec.containers[] | [$p, .name, (.resources.requests.cpu // "-"), (.resources.limits.memory // "-")] | @tsv'
```

## jq - Inspect Docker Containers

`docker inspect` returns an array even for one container, so every filter starts with `.[]`.

```
docker inspect $(docker ps -aq) | jq -r '.[] | [.Name, .State.Status, .Config.Image] | @tsv'
```

Explain why containers stopped. Exit code 137 means the kernel OOM-killed it or it was hard-killed.

```
docker inspect $(docker ps -aq) | jq -r '.[] | select(.State.Running | not) | "\(.Name) exited with \(.State.ExitCode)"'
```

Container IPs live under a network name you do not know in advance, so `to_entries` is the only way to reach them generically:

```
docker inspect $(docker ps -q) | jq -r '.[] | "\(.Name)\t\(.NetworkSettings.Networks | to_entries[] | .value.IPAddress)"'
```

List writable mounts, which is where state that survives a container rebuild actually lives:

```
docker inspect $(docker ps -q) | jq -r '.[] | .Name as $n | .Mounts[] | select(.RW) | "\($n) \(.Source) -> \(.Destination)"'
```

Find containers with no memory limit, since one of those can take a whole on-premise host down:

```
docker inspect $(docker ps -q) | jq -r '.[] | select(.HostConfig.Memory == 0) | .Name'
```

`docker ps --format json` emits one object per line rather than an array, so use `-s` when you need to aggregate across them:

```
docker ps -a --format json | jq -r 'select(.State != "running") | "docker start \(.Names)"'
```

## jq - Walk a REST API Response

Summarise an envelope before deciding whether to page again. Computing the check inside jq keeps the pagination logic out of the shell.

```
curl -s https://api.example.com/v1/items | jq -c '{page, total, returned: (.items | length), has_more: (.page * 25 < .total)}'
```

`if/elif/else/end` classifies records in one pass, and always needs the `end`:

```
curl -s https://api.example.com/v1/items | jq -r '.items[] | if .cpu > 300 then "\(.name) HOT" elif .cpu == 0 then "\(.name) IDLE" else "\(.name) ok" end'
```

Turn a query response straight into the follow-up commands, with `@sh` guarding against hostile values in the data:

```
curl -s https://api.example.com/v1/items | jq -r '.items[] | select(.state == "failed") | @sh "curl -X POST https://api.example.com/restart/\(.id)"'
```

Gate a health check on the response body rather than on the HTTP status, so a 200 with a degraded payload still fails:

```
curl -s https://api.example.com/health | jq -e '.status == "ok"' >/dev/null || echo "service degraded"
```
