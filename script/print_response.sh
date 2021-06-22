#!/bin/sh
#Usage: sh print_response.sh user password url

user=$1
password=$2
url=$3

rm -f .pymultimatic-cookie

token=$(
  curl \
    -c .pymultimatic-cookie \
    -s \
    -X POST \
    -H "Content-Type:application/json" -H "Accept:application/json" \
    -d '{ "smartphoneId": "pymultiMATIC", "username": "'$user'", "password": "'$password'" }' \
    'https://smart.vaillant.com/mobile/api/v4/account/authentication/v1/token/new' \
    | jq -r '.body.authToken'
)

curl \
  -b .pymultimatic-cookie \
  -c .pymultimatic-cookie \
  -X POST \
  -H "Content-Type:application/json" -H "Accept:application/json" \
  -d '{ "smartphoneId": "pymultiMATIC", "username": "'$user'", "authToken": "'$token'" }' \
  "https://smart.vaillant.com/mobile/api/v4/account/authentication/v1/authenticate"

curl \
  -b .pymultimatic-cookie \
  -X GET \
  -H "Content-Type:application/json" -H "Accept:application/json" \
  "$url"

rm -f .pymultimatic-cookie