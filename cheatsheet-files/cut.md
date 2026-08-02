# cut

cut extracts sections from each line of input, selected by field, character, or byte position. It is the quickest way to pull columns out of delimited data when awk would be overkill.

#platform/multiple #target/Shell #cat/TextProcessing

% cut, columns, fields, delimiter, text processing

## cut - Extract a Field by Delimiter

Select a field with `-f`, using `-d` to say what separates the fields.

```
cut -d: -f1 /etc/passwd
```

Extract the second column of a CSV:

```
cut -d, -f2 data.csv
```

## cut - Extract Several Fields

Give a comma-separated list of field numbers. They are always emitted in file order, regardless of how they are listed.

```
cut -d: -f1,3,7 /etc/passwd
```

Select a range of fields:

```
cut -d, -f2-4 data.csv
```

Select from a field to the end of the line:

```
cut -d, -f3- data.csv
```

Select from the start up to a field:

```
cut -d, -f-2 data.csv
```

## cut - Use a Tab Delimiter

Tab is the default delimiter, so no `-d` is needed for TSV input.

```
cut -f2 data.tsv
```

State it explicitly when it aids readability:

```
cut -d$'\t' -f2 data.tsv
```

## cut - Use a Space Delimiter

Quote the space so the shell passes it through. Note that cut treats every single space as a separator and does not collapse runs of them, which is why awk is the better choice for whitespace-aligned output.

```
cut -d' ' -f1 access.log
```

Squeeze repeated spaces first if the columns are padded:

```
tr -s ' ' < report.txt | cut -d' ' -f2
```

## cut - Extract Characters by Position

Select character positions with `-c` instead of fields.

```
cut -c1-10 timestamps.log
```

Take a single character:

```
cut -c1 answers.txt
```

Take everything from a position to the end of the line:

```
cut -c20- data.txt
```

Combine several ranges:

```
cut -c1-4,10-12 fixed-width.txt
```

## cut - Extract Bytes

Select byte positions with `-b`. This differs from `-c` on multi-byte encodings such as UTF-8, where it can split a character.

```
cut -b1-8 data.bin
```

## cut - Invert the Selection

Print every field except the ones selected.

```
cut -d, -f2 --complement data.csv
```

## cut - Skip Lines Without the Delimiter

By default a line with no delimiter is printed whole. Use `-s` to drop those lines instead, which filters out headers and comments.

```
cut -d: -sf1 config.txt
```

## cut - Change the Output Delimiter

Emit a different separator from the one used to split the input.

```
cut -d: -f1,7 --output-delimiter=' -> ' /etc/passwd
```

Convert CSV to TSV:

```
cut -d, -f1-3 --output-delimiter=$'\t' data.csv
```

## cut - Cut Command Output

Read from standard input through a pipe when no file is given.

```
ps aux | cut -c1-80
```

Pull the process IDs out of a listing:

```
ps -ef | tr -s ' ' | cut -d' ' -f2
```

## cut - Extract from Multiple Files

Pass several files; cut concatenates the results without printing filenames.

```
cut -d, -f1 january.csv february.csv
```
