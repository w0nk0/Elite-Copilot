__author__ = 'W0nk0'

def address():
    import os
    result = []
    os.system('ipconfig > ipconf.txt')
    with open('ipconf.txt','rt') as lines:
        for line in lines:
            if 'IPv4' in line:
                if ":" in line:
                    result.append(line.split(':')[1].strip())

    return "\n".join(result)

if __name__ == "__main__":
    print "'"+address()+"'"
