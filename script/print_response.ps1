$user=$args[0]
$password=$args[1]
$url=$args[2]

$payload=@"
{
\"smartphoneId\": \"pymultiMATIC\", 
\"username\": \"$user\", 
\"password\": \"$password\" 
}
"@

$token_response = curl.exe -s `
			-c .pymultimatic-cookie `
			-X POST `
			-H "Content-Type:application/json" -H "Accept:application/json" `
			-d $payload `
			"https://smart.vaillant.com/mobile/api/v4/account/authentication/v1/token/new" | ConvertFrom-Json

$token=$token_response.body.authToken

$payload=@"
{
\"smartphoneId\": \"pymultiMATIC\", 
\"username\": \"$user\", 
\"authToken\": \"$token\" 
}
"@

curl.exe -s `
 -b .pymultimatic-cookie `
 -c .pymultimatic-cookie `
 -X POST `
 -H "Content-Type:application/json" -H "Accept:application/json" `
 -d "$payload" `
 "https://smart.vaillant.com/mobile/api/v4/account/authentication/v1/authenticate"


$response=curl.exe -s `
 -b .pymultimatic-cookie `
 -X GET `
 -H "Content-Type:application/json" -H "Accept:application/json" `
 "$url"

Write-Host "$response"