from PyTib.common import write_file, open_file, is_tibetan_letter
import os
import unicodedata
import re

def is_tib_char(char):
    if not unicodedata.name(char):
        print('char', end=' ')
        return False
    elif 'TIBETAN' in unicodedata.name(char):
        return True
    else:
        print(char)
        return False

tags = ['d', 'g', 'j', 'k', 'l', 'n', 'p', 'r', 's', 't', 'w', 'y']
tib = [' ', '་', '།', '༄', '༣', '༅', '༽', '༼', '༨', '༧', '༡', '༦', '༩', '༥', '༢', '༠', '༤']
non_tib = []
path = './raw_data/volumes'
for f in os.listdir(path):
    print(f)
    content = open_file(path+'/'+f).replace('\\', '')
    #content = re.sub(r' ?\, ?', r'\, ', content)
    write_file(path+'/'+f, content)
    #content = open_file(path + '/' + f)
    for c in content:
        if not is_tibetan_letter(c) and c not in tib and c not in tags:
            non_tib.append(c)
print(set(non_tib))