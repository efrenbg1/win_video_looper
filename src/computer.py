import os
import sys

_ip = ""


def ip():
    global _ip
    if _ip != "":
        return _ip
    try:
        import subprocess
        if sys.platform == 'win32':
            ip = subprocess.Popen(['netstat', '-rn'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ip, _ = ip.communicate()
            ip = ip[ip.find(b'0.0.0.0'):]
            ip = ip[:ip.find(b'\r\n')]
            ip = ip.split(b' ')
            while b'' in ip:
                ip.remove(b'')
            ip = ip[3].decode('utf-8')
            _ip = ip
        else:
            ip = subprocess.Popen(['hostname', '--all-ip-addresses'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ip, _ = ip.communicate()
            ip = ip.split(b' ')
            _ip = ip[0].decode('utf-8')
    except Exception as e:
        print(e)
        _ip = name()
        pass

    return _ip


def name():
    if sys.platform == 'win32':
        return os.environ['COMPUTERNAME']
    else:
        return os.uname()[1]


if __name__ == "__main__":
    print(ip())
    print(name())
