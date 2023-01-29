#!/bin/bash

version=$(python3 setup.py -V)
result=$(curl -s https://pypi.org/pypi/pymultiMATIC/json | jq -r '.releases | keys[]' | grep -w $version)

if [ -z "$result" ]
then
  echo Version "$version" not found in pypi, all good
  exit 0
else
  echo Version "$version" already exist in pypi
  exit 1
fi