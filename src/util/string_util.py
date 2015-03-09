__author__ = 'parker'

def convert_latin1(s):
    if(s == None):
        return None
    s = s.decode('latin1').encode('UTF-8')
    return s