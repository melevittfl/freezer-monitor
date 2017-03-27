import socket
import re


def found_kitchen_sonos(usn):
    msg = \
        'M-SEARCH * HTTP/1.1\r\n' \
        'HOST:239.255.255.250:1900\r\n' \
        'ST:upnp:rootdevice\r\n' \
        'MX:2\r\n' \
        'MAN:"ssdp:discover"\r\n'

    kitchen_usn = re.compile(usn)
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.settimeout(5)
    s.sendto(msg.encode('utf-8'), ('239.255.255.250', 1900) )

    attempts = 0

    while attempts < 3:
        try:
            data, addr = s.recvfrom(65507)
            #print (addr, data)
            if kitchen_usn.search(data):
                ip, port = addr
                return True
        except socket.timeout:
            attempts += 1


    return False

if __name__ == '__main__':
    usn = b'5CAAFD77ADE401400'
    print("Found Kitchen Sonos: {0}".format(found_kitchen_sonos(usn)))
