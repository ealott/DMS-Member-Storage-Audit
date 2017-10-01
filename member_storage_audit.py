#!/usr/bin/python

import requests,json,zebra


qr_data = (input('Please scan QR code: ')).strip().split(',')

rfid = ''.join(qr_data[1:2])

print("Member's RFID: " + rfid)



url = "http://192.168.200.130:8080/api/v1/lookupByRfid"
payload = "rfid=" + rfid
headers = {
    'content-type': "application/x-www-form-urlencoded",
       }
response = requests.request("POST", url, data=payload, headers=headers)

response_body = json.loads(response.text)

#print(response_body)


member_active = response_body['result']['accessGranted']

if member_active:
    print("Member active")
    
else:
    print("Member not active, or data lookup failed.")
    print ("Member name: " + response_body['result']['user']['fullName'])
    
label = ""

#https://pypi.python.org/pypi/zebra/
#pip-3.2 install zebra
z = zebra('zebra_test')
z.output(label)
