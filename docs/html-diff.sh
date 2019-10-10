#!/bin/bash

diffs=$(diff <(find tmp/html -type f -name '*.html' -exec md5sum {} + | sort -k 2 | sed 's/ .*\// /') <(find build/html -type f -name '*.html' -exec md5sum {} + | sort -k 2 | sed 's/ .*\// /'))

if [ "$diffs" = "" ]
then
  exit 0
fi
echo "$diffs"
exit 1