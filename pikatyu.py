import zipfile
import timeit

start = timeit.default_timer()

def bytes_parse(data, bytes_format):
    R = []
    pointer = 0
    for p in bytes_format:
        R.append(data[pointer:pointer+p])
        pointer += p
    bottom = data[pointer:]
    if(len(bottom) != 0):
        R.append(bottom)
    return R

def _gen_crc(crc):
    for j in range(8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xEDB88320
        else:
            crc >>= 1
    return crc

def main():
    crctable = list(map(_gen_crc, range(256)))
    file_name = "sample04.zip"
    f = open(file_name, "rb")
    buf = f.read()
    f.close()
    buf_parsed = bytes_parse(buf, (4, 2, 2, 2, 2, 2, 4, 4, 4, 2, 2))
    last_mod_file_time = int.from_bytes(buf_parsed[4], "little")
    compressed_size = int.from_bytes(buf_parsed[7], "little")
    file_name_length = int.from_bytes(buf_parsed[9], "little")
    extra_field_length = int.from_bytes(buf_parsed[10], "little")
    p = file_name_length+extra_field_length
    czy = buf_parsed[11][p:p+compressed_size]
    additional_data = czy[:12]
    for i in range(0, 1000000):
        password = str(i).encode("utf-8")
        key0 = 305419896
        key1 = 591751049
        key2 = 878082192
        for p in password:
            key0 = (key0 >> 8) ^ crctable[(key0 ^ p) & 0xFF]
            key1 = (key1 + (key0 & 0xFF)) & 0xFFFFFFFF
            key1 = (key1 * 134775813 + 1) & 0xFFFFFFFF
            key2 = (key2 >> 8) ^ crctable[(key2 ^ key1 >> 24) & 0xFF]
        # Decrypt
        result = bytearray()
        append = result.append
        for c in additional_data:
            k = key2 | 2
            c ^= ((k * (k^1)) >> 8) & 0xFF
            key0 = (key0 >> 8) ^ crctable[(key0 ^ c) & 0xFF]
            key1 = (key1 + (key0 & 0xFF)) & 0xFFFFFFFF
            key1 = (key1 * 134775813 + 1) & 0xFFFFFFFF
            key2 = (key2 >> 8) ^ crctable[(key2 ^ key1 >> 24) & 0xFF]
            append(c)
        if(buf_parsed[4] == result[-2:]):
            try:
                with zipfile.ZipFile(file_name) as pass_zip:
                    pass_zip.extractall("./", pwd=password)
                    print(password)
                    break
            except:
                pass

main()
stop = timeit.default_timer()
print(stop-start)