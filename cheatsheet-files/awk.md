# awk

awk is a pattern-scanning and text-processing language. It splits each input line into fields and runs actions on the lines that match a pattern, which makes it the usual tool for extracting and summarising columns of command output.

#platform/multiple #target/Shell #cat/TextProcessing

% awk, text processing, columns, fields, reporting

## awk - Print a Column

Print a single field from each line. Fields are split on whitespace by default and numbered from 1.

```
awk '{print $1}' access.log
```

Print several fields, separated by a space:

```
awk '{print $1, $4}' access.log
```

Print the whole line with `$0`:

```
awk '{print $0}' access.log
```

## awk - Set the Field Separator

Split on a character other than whitespace with `-F`.

```
awk -F: '{print $1}' /etc/passwd
```

Split on a comma for CSV input:

```
awk -F, '{print $2}' data.csv
```

Use a regular expression as the separator, here one or more colons or spaces:

```
awk -F'[: ]+' '{print $1}' input.txt
```

## awk - Print the Last Field

`NF` holds the number of fields, so `$NF` is the last one.

```
awk '{print $NF}' access.log
```

Print the second-to-last field:

```
awk '{print $(NF-1)}' access.log
```

## awk - Filter Lines by Pattern

Give a pattern with no action and awk prints the matching lines.

```
awk '/ERROR/' app.log
```

Apply an action only to matching lines:

```
awk '/ERROR/ {print $2}' app.log
```

Match against one field rather than the whole line:

```
awk '$3 ~ /timeout/ {print $1}' app.log
```

## awk - Filter with a Numeric Comparison

Compare a field numerically and print only the lines that qualify.

```
awk '$5 > 1000 {print $1, $5}' report.txt
```

Combine conditions with `&&` and `||`:

```
awk '$3 == "GET" && $9 == 404 {print $7}' access.log
```

## awk - Use the Line Number

`NR` is the current record number, so it can skip or select lines.

```
awk 'NR > 1 {print $1}' data.csv
```

Print a single line:

```
awk 'NR == 10' file.txt
```

Print a range of lines:

```
awk 'NR >= 5 && NR <= 10' file.txt
```

## awk - Sum a Column

Accumulate a running total and print it once the input is exhausted.

```
awk '{sum += $2} END {print sum}' data.txt
```

Print the average instead:

```
awk '{sum += $2} END {print sum / NR}' data.txt
```

## awk - Count Occurrences

Use an associative array keyed on a field to tally distinct values, replacing `sort | uniq -c`.

```
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log
```

Sort the tally afterwards:

```
awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -rn | head
```

## awk - Run Setup and Teardown Blocks

`BEGIN` runs before the first line and `END` after the last, which is where headers and totals belong.

```
awk 'BEGIN {print "user shell"} {print $1, $7} END {print NR " rows"}' FS=: /etc/passwd
```

Set variables in `BEGIN`:

```
awk 'BEGIN {FS=":"; OFS=" -> "} {print $1, $6}' /etc/passwd
```

## awk - Format Output with printf

`printf` gives control over width, alignment, and decimal places, and does not add a newline on its own.

```
awk '{printf "%-15s %8.2f\n", $1, $2}' data.txt
```

Print a percentage:

```
awk '{printf "%s: %.1f%%\n", $1, $2 * 100 / $3}' data.txt
```

## awk - Set the Output Field Separator

`OFS` controls what separates fields on output, but it only takes effect when the line is rebuilt.

```
awk 'BEGIN {FS=","; OFS="\t"} {$1=$1; print}' data.csv
```

## awk - Count Matching Lines

Increment a counter and print it at the end, the awk equivalent of `grep -c`.

```
awk '/ERROR/ {n++} END {print n+0}' app.log
```

## awk - Print Unique Lines

Track seen lines in an array to deduplicate without sorting, preserving the original order.

```
awk '!seen[$0]++' file.txt
```

Deduplicate on one field only:

```
awk '!seen[$1]++' access.log
```

## awk - Use String Functions

`length` returns the length of a field or of the whole line.

```
awk 'length($0) > 80 {print FILENAME ":" NR}' *.py
```

`substr` extracts part of a field, indexed from 1:

```
awk '{print substr($1, 1, 10)}' timestamps.txt
```

`gsub` substitutes every match in place and returns the count:

```
awk '{gsub(/,/, ""); print $1 + 0}' amounts.txt
```

`split` breaks a field into an array:

```
awk '{n = split($1, parts, "."); print parts[n]}' hostnames.txt
```

## awk - Pass a Shell Variable In

Use `-v` to define an awk variable, which avoids quoting problems with shell interpolation.

```
awk -v threshold=500 '$2 > threshold {print $1}' data.txt
```

## awk - Process Multiple Files

`FILENAME` holds the current file and `FNR` restarts at 1 for each one.

```
awk 'FNR == 1 {print "== " FILENAME}  /error/ {print FNR ": " $0}' *.log
```

## awk - Change the Record Separator

Set `RS` to treat blank-line-separated blocks as single records.

```
awk 'BEGIN {RS=""; FS="\n"} {print $1}' paragraphs.txt
```
