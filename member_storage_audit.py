#!/usr/bin/python

import requests,json,socket
from time import gmtime, strftime
import pprint
import logging
import csv

logging.basicConfig(filename='storage_audit.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)


current_time = strftime("%a, %d %b %Y %X +0000", gmtime())
TCP_IP = '192.168.206.120' #was '192.168.204.222'
TCP_PORT = 9100
BUFFER_SIZE = 1024


def split_barcode(storage_bin_qr_code):
    qr_data = storage_bin_qr_code.strip().strip("http://").split(',')    
    rfid = ''.join(qr_data[1:2])
    firstName = ''.join(qr_data[4:5])
    lastName = ''.join(qr_data[5:])
    phone = ''.join(qr_data[2:3])
    
    #some, but not all storage tags substitute @ in the email with "
    if ('"') in qr_data[3:4]:
        email = ''.join(qr_data[3:4]).replace('"', '@')
    else:
        email = ''.join(qr_data[3:4])

    member_details = {
     "rfid": rfid,
     "first name": firstName,
     "last name":  lastName,
     "email": email,
     "phone": phone
    }

    return member_details

def query_member_api(member_info):
    url = "http://192.168.200.32:8080/api/v1/users/lookupByFields"
    #payload = "rfid=10284295&username=perpetual&firstName=mike&lastName=kelp&email=mike.kelp@gmail.com"
    logging.info("Member info supplied to query_member_api: " + str(member_info))
    payload = 'rfid=' + member_info['rfid'] + '&firstName=' + member_info['first name'] + "&lastName=" + member_info['last name'] + "&email=" + member_info['email']

    logging.info("Payload sent to API: " + payload)

    headers = {
        'cache-control':"no-cache",
        'content-type': "application/x-www-form-urlencoded",
       }

    try:   
        response = requests.request("POST", url, data=payload, headers=headers)
        response_body = json.loads(response.text)

    except Exception as e:
        logging.info("Exception: " + e)


    logging.info("API response: " + str(response.text))
    logging.info("API Response Body: " + str(response_body))

    return response_body['result']


def print_to_zebra(firstName,lastName,email,phone,rfid):
    #note that the LP 2844 only supports EPL, not ZPL!
    #EPL references: https://en.wikipedia.org/wiki/Eltron_Programming_Language 
    # https://www.zebra.com/content/dam/zebra/manuals/en-us/printer/epl2-pm-en.pdf
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

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        s.send(bytes(epl, "utf-8"))
        s.close()
    except Exception as e:
        print(e)


def main():
#network settings for zebra LP 2844 printer (supports EPL only)
    TCP_IP = '192.168.206.120' #was '192.168.204.222'
    TCP_PORT = 9100
    BUFFER_SIZE = 1024

    qr_codes = []
    active_members=[]
    inactive_members = []
    
    while True:

        qr_data = (input('Please scan QR codes.  Type "done" (no quotes) when done scanning.\n'))

        if not qr_data.startswith('done'):
            qr_codes.append(qr_data)
        else:
            break

    print("Looking up membership status from " + str(len(qr_codes)) + " storage bin tags...")

    for qr_code in qr_codes:
        #print(split_barcode(qr_code))
        member_api_data = query_member_api((split_barcode(qr_code)))
        if member_api_data :
            active_members.append(split_barcode(qr_code))
        else:
            inactive_members.append(split_barcode(qr_code))

    print("Found " + str(len(active_members)) + " active members and the following " + str(len(inactive_members)) +" potentially inactive members.")
    pprint.pprint(inactive_members)
    logging.info("Active Members: " + str(active_members))
    logging.info("Inactive Members: " + str(inactive_members))
    write_to_csv(inactive_members)

    to_print = (input("Would you like to send inactive member details to the Zebra printer? y for yes, anything else for no.")).upper()
    if to_print.startswith('Y'):
        for member_info in inactive_members:
            print_to_zebra(
                member_info["first name"],
                member_info["last name"],
                member_info["email"],
                member_info["phone"],
                member_info["rfid"]
                )

def write_to_csv(member_list):
    with open('inactive_members.csv', 'w') as csvfile:
        fieldnames = ['first name', 'last name','email','phone','rfid']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(member_list)


if __name__ == "__main__":
    main()
