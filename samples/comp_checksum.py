import sys
from htheatpump.htheatpump import calc_checksum


#header = b"\x02\xfd\xe0\xd0\x00\x00"
#header = b"\x02\xfd\xe0\xd0\x04\x00"
#header = b"\x02\xfd\xe0\xd0\x08\x00"
#header = b"\x02\xfd\xe0\xd0\x02\x00"
header = b"\x02\xfd\xe0\xd0\x01\x00"


# Main program
def main():
    payload = "~" + sys.argv[1] + ";\r\n"
    payload = payload.encode("ascii")
    payload_len = len(payload) - 1
    print(header + bytes([payload_len]) + payload)
    checksum = calc_checksum(header + bytes([payload_len]) + payload)
    print(hex(checksum))


if __name__ == "__main__":
    main()
