import socket
TCP_IP = '192.168.204.222'
TCP_PORT = 9100
BUFFER_SIZE = 1024

#note that the LP 2844 only supports EPL, not ZPL!

#this will print an example label
epl = """
N
A50,0,0,1,1,1,N,"Example 1"
A50,50,0,2,1,1,N,"Example 2"
A50,100,0,3,1,1,N,"Example 3"
A50,150,0,4,1,1,N,"Example 4"
A50,200,0,5,1,1,N,"EXAMPLE 5"
A50,300,0,3,2,2,R,"Example 6"
P1
"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(bytes(epl, "utf-8"))
s.close()
