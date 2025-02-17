import requests
import json

url = "http://localhost:3000/api/users"

payload = {}
headers = {
  'x-tenant-id': 'd9c08603-4039-4b7d-8afe-29ff53ef06f8',
  'Authorization': 'Bearer GF0dXMiOjF9LCJpYXQiOjE3Mzk1ODgwODAsImV4cCI6MTc0MDE5Mjg4MH0.b6F8rQ1Q4ZD0YJ6dsOYsp5yAmBPaz2c5gC9lo-kJ7xk',
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

