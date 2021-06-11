import os
import sys


def ip():
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
        else:
            ip = subprocess.Popen(['hostname', '--all-ip-addresses'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ip, _ = ip.communicate()
            ip = ip.split(b' ')
            ip = ip[0].decode('utf-8')
    except Exception as e:
        print(e)
        ip = name()
        pass

    return ip


def name():
    if sys.platform == 'win32':
        return os.environ['COMPUTERNAME']
    else:
        return os.uname()[1]


if __name__ == "__main__":
    print(ip())
    print(name())
