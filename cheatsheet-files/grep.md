# grep

grep searches files or standard input for lines matching a pattern and prints them. It is the standard tool for finding text in logs, source trees, and command output.

#platform/multiple #target/Shell #cat/TextProcessing

% grep, search, regex, text processing, logs

## grep - Search a File for a Pattern

Print every line in a file that contains the pattern.

```
grep "error" /var/log/syslog
```

Search several files at once, prefixing each match with its filename:

```
grep "timeout" /var/log/*.log
```

## grep - Ignore Case

Match without regard to upper or lower case.

```
grep -i "warning" app.log
```

## grep - Search Recursively

Search every file under a directory tree.

```
grep -r "TODO" .
```

Follow symbolic links while recursing:

```
grep -R "TODO" .
```

## grep - Show Line Numbers

Prefix each match with its line number in the file.

```
grep -n "func main" main.go
```

## grep - Invert the Match

Print the lines that do not match the pattern, useful for filtering out noise.

```
grep -v "healthcheck" access.log
```

Chain inversions to drop several patterns:

```
grep -v "healthcheck" access.log | grep -v "/favicon.ico"
```

## grep - Count Matches

Print how many lines matched instead of the lines themselves.

```
grep -c "ERROR" app.log
```

## grep - List Only Filenames

Print the names of files that contain at least one match, not the matching lines.

```
grep -rl "api_key" .
```

Print the files with no match instead:

```
grep -rL "license" src/
```

## grep - Match Whole Words

Require the pattern to be a complete word, so `cat` does not match `concatenate`.

```
grep -w "cat" notes.txt
```

Require the pattern to match the entire line:

```
grep -x "done" status.txt
```

## grep - Use Extended Regular Expressions

Enable extended regex so `|`, `+`, `?`, and grouping work without backslashes.

```
grep -E "error|fatal|panic" app.log
```

Match an IP address:

```
grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" access.log
```

## grep - Match a Fixed String

Treat the pattern literally, so regex metacharacters have no special meaning. This is also faster on large inputs.

```
grep -F "config[0].value" settings.txt
```

## grep - Print Only the Matching Part

Print just the text that matched rather than the whole line.

```
grep -o "[a-z]*@[a-z.]*" contacts.txt
```

Combine with `sort` and `uniq` to tally distinct matches:

```
grep -oE "HTTP/1.1\" [0-9]{3}" access.log | sort | uniq -c | sort -rn
```

## grep - Show Surrounding Context

Print lines after each match to see what followed an error.

```
grep -A 5 "Exception" app.log
```

Print lines before the match:

```
grep -B 3 "Exception" app.log
```

Print lines on both sides:

```
grep -C 3 "Exception" app.log
```

## grep - Filter Which Files Are Searched

Restrict a recursive search to certain filenames.

```
grep -r --include="*.py" "import requests" .
```

Skip files or directories instead:

```
grep -r --exclude-dir={.git,node_modules} "password" .
```

## grep - Search for Several Patterns

Supply multiple patterns with repeated `-e` flags.

```
grep -e "error" -e "warning" app.log
```

Read the patterns from a file, one per line:

```
grep -f patterns.txt app.log
```

## grep - Use in a Conditional

Suppress all output and rely on the exit status, which is 0 when something matched.

```
grep -q "ready" status.log && echo "service is up"
```

## grep - Search Command Output

Filter the output of another command through a pipe.

```
ps aux | grep -i nginx
```

Exclude the grep process itself from the results:

```
ps aux | grep "[n]ginx"
```

## grep - Search Compressed Files

Search gzip-compressed logs without decompressing them first.

```
zgrep "error" /var/log/syslog.2.gz
```

## grep - Use Perl-Compatible Regular Expressions

Enable PCRE for lookarounds, lazy quantifiers, and `\d` style classes.

```
grep -P "\d{4}-\d{2}-\d{2}" app.log
```

Match a value that follows a key, without printing the key:

```
grep -oP "(?<=user=)\w+" auth.log
```
