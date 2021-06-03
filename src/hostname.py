_hostname = ""


def get():
    global _hostname
    if _hostname != "":
        return _hostname
    import sys
    try:
        import subprocess
        if sys.platform == 'win32':
            hostname = subprocess.Popen(['netstat', '-rn'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            hostname, _ = hostname.communicate()
            hostname = hostname[hostname.find(b'0.0.0.0'):]
            hostname = hostname[:hostname.find(b'\r\n')]
            hostname = hostname.split(b' ')
            while b'' in hostname:
                hostname.remove(b'')
            hostname = hostname[3].decode('utf-8')
            _hostname = hostname
        else:
            hostname = subprocess.Popen(['hostname', '--all-ip-addresses'],  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            hostname, _ = hostname.communicate()
            hostname = hostname.split(b' ')
            _hostname = hostname[0].decode('utf-8')
    except Exception as e:
        print(e)
        import os
        _hostname = os.environ['COMPUTERNAME']
        pass

    return _hostname


if __name__ == "__main__":
    print(get())
