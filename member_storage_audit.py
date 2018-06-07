#!/usr/bin/python
from __builtin__ import raw_input

import requests
import json
import socket
import ConfigParser
from time import gmtime, strftime

#Read config file
config = ConfigParser.ConfigParser()
config.read("config.ini")


def lookup_barcode(storage_bin_qr_code):
    rfid = ''.join(storage_bin_qr_code[1:2])
    firstname = ''.join(storage_bin_qr_code[4:5])
    lastname = ''.join(storage_bin_qr_code[5:])
    phone = ''.join(storage_bin_qr_code[2:3])
    
    #some, but not all storage tags substitute @ in the email with "
    if ('"') in storage_bin_qr_code[3:4]:
        email = ''.join(storage_bin_qr_code[3:4]).replace('"', '@')
    else:
        email = ''.join(storage_bin_qr_code[3:4])

    print("Member's RFID: " + rfid)
    print("First name: " + firstname)
    print("Last name: " + lastname)
    print("Email: " + email)

    response = query_member_info_api("rfid",rfid)
    response_body = json.loads(response.text)
    #print(response_body)

    if response_body['result']:
        print("Member active" + "\n")

    else:
        response = query_member_info_api("phone", phone)
        response_body = json.loads(response.text)
        if response_body['result']:
            print("Member active" + "\n")
        else:
            response = query_member_info_api("email", email)
            response_body = json.loads(response.text)
            if response_body['result']:
                print("Member active" + "\n")

            else:  # test data for inactive member: dms,00072497335,1972123456789,test@gmail.com,John,Smith
                print("Member not active, or data lookup failed.")
                print("Member name: " + firstname + " " + lastname)
                print("Member email: " + email)
                print("Member phone: " + phone + "\n")

        inactive_member_info = {"First name": firstname, "Last name": lastname, "email": email, "Phone": phone}
        inactive_members.append(inactive_member_info)

        print_to_zebra(firstname, lastname, email, phone, rfid, TCP_IP, TCP_PORT)


def query_member_info_api(member_data_type, member_data):
    #TODO: move API settings to config file
    api_url = "http://192.168.200.32:8080/api/v1/users/lookupByFields"
    payload = member_data_type + "=" + member_data
    headers = {
        'cache-control':"no-cache",
        'content-type': "application/x-www-form-urlencoded",
       }
    response = requests.request("POST", api_url, data=payload, headers=headers)
    
    #print(response)
    #print(response.text)
    return response

        
def print_to_zebra(firstName,lastName,email,phone,rfid,TCP_IP,TCP_PORT):

        #note that the LP 2844 only supports EPL, not ZPL!
        #EPL references: https://en.wikipedia.org/wiki/Eltron_Programming_Language https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf
        #Ah_pos,v_pos,rotation,font,h_mult,v_mult,reverse,"text" - ASCII text


        epl = (
        "N" "\n"
        'A10,25,0,5,1,1,N,"BIN OWNER INACTIVE"' "\n"
        'A10,100,0,4,1,1,N,"SCAN DATE: '  + str(current_time) + '"\n'
        'A15,150,0,4,1,1,N,"MEMBER INFO:"' "\n"
        'A15,200,0,3,1,1,N,"NAME: '  + str(firstName + " " + lastName) + '"\n'
        'A15,250,0,3,1,1,N,"EMAIL: '  + str(email) + '"\n'
        'A15,300,0,3,1,1,N,"PHONE: '  + str(phone) + '"\n'
        "LO,600,750,20" "\n"
        'B50,800,0,3,3,7,200,B,"' + str(rfid) + '"\n'
        "P1" "\n"
        )


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(bytes(epl, "utf-8"))
        s.close()

#TODO: break printer settings into cfg file
#network settings for zebra LP 2844 printer (supports EPL only)
TCP_IP = '192.168.206.120' #was '192.168.204.222'
TCP_PORT = 9100
BUFFER_SIZE = 1024

inactive_members = []

print('Begin scanning storage bins.  Type "exit" and press enter to exit.')

while True:
    
    current_time = strftime("%a, %d %b %Y %X +0000", gmtime())
    print(current_time)

    qr_data = (raw_input('Please scan QR code: ')).strip().split(',')

    #qr_data = string.replace(qr_raw, '"', '@') #convert the " in the email address to a proper @
    
    if qr_data != 'exit':
        lookup_barcode(qr_data)
    
    else:
        break

