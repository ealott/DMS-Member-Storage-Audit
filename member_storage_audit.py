#!/usr/bin/python

import requests,json,socket
from time import gmtime, strftime


#network settings for zebra LP 2844 printer (supports EPL only)
TCP_IP = '192.168.204.222'
TCP_PORT = 9100
BUFFER_SIZE = 1024

print('Please begin scanning storage bins.  Type "exit" and press enter to exit.')

while True:
    
    current_time = strftime("%a, %d %b %Y %X +0000", gmtime())
    print (current_time)

    qr_data = (input('Please scan QR code: ')).strip().split(',')
    
    if qr_data == 'exit':
        break
    
    rfid = ''.join(qr_data[1:2])
    firstName = ''.join(qr_data[4:5])
    lastName = ''.join(qr_data[5:])
    email = ''.join(qr_data[3:4])
    phone = ''.join(qr_data[2:3])

    print("Member's RFID: " + rfid)

    url = "http://192.168.200.130:8080/api/v1/lookupByRfid"
    payload = "rfid=" + rfid
    headers = {
    'content-type': "application/x-www-form-urlencoded",
       }
    response = requests.request("POST", url, data=payload, headers=headers)

    response_body = json.loads(response.text)

    #print(response.text)
    #print(response_body)

    member_active = response_body['result']['accessGranted']


    if member_active: 
        print("Member active" + "\n")
    
    else: #test data for inactive member: dms,00072497335,1972123456789,test@gmail.com,John,Smith
        print("Member not active, or data lookup failed.")
        print("Member name: " + firstName + " " + lastName)
        print("Member email: " + email)
        print("Member phone: " + phone + "\n")


        #note that the LP 2844 only supports EPL, not ZPL!
        #EPL references: https://en.wikipedia.org/wiki/Eltron_Programming_Language https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf
        #Ah_pos,v_pos,rotation,font,h_mult,v_mult,reverse,"text" - ASCII text

        epl = (
        "N" "\n"
        'A0,25,0,5,1,1,N,"BIN OWNER INACTIVE"' "\n"
        'A0,100,0,4,1,1,N,"SCAN DATE: '  + str(current_time) + '"\n'
        'A5,150,0,4,1,1,N,"MEMBER INFO:"' "\n"
        'A5,200,0,3,1,1,N,"NAME: '  + str(firstName + " " + lastName) + '"\n'
        'A5,250,0,3,1,1,N,"EMAIL: '  + str(email) + '"\n'
        'A5,300,0,3,1,1,N,"PHONE: '  + str(phone) + '"\n'
        "LO,600,750,20" "\n"
        'B50,800,0,3,3,7,200,B,"' + str(rfid) + '"\n'
        "P1" "\n"
        )


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(bytes(epl, "utf-8"))
        s.close()

