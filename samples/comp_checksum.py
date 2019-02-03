import sys


def calc_checksum(s):
    """ Function that calculates the checksum of a provided bytes array.

    :param s: Byte array from which the checksum should be computed.
    :type s: bytes
    :returns: The computed checksum as ``int``.
    :rtype: ``int``
    """
    checksum = 0x0
    for i in range(0, len(s)):
        databyte = s[i]
        checksum ^= databyte
        databyte = (databyte << 1) & 0xff
        checksum ^= databyte
    return checksum


header = b"\x02\xfd\xe0\xd0\x01\x00"


# Main program
def main():
    payload = "~" + sys.argv[1] + ";\r\n"
    payload = payload.encode("ascii")
    #print(payload)
    payload_len = len(payload) - 1
    print(header + bytes([payload_len]) + payload)
    checksum = calc_checksum(header + bytes([payload_len]) + payload)
    print(hex(checksum))
    sys.exit(0)


if __name__ == "__main__":
    main()
