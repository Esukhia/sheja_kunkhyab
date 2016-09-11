from PyTib.common import write_file, open_file, is_tibetan_letter, tib_sort
import os
import unicodedata
import re
from collections import defaultdict


def find_no_space_after_tag(string):
    tags = re.findall(r'<[a-z]+ ?[^>]+>', string)
    for t in tags:
        truc = re.findall(r'<[a-z]+(.)', t)
        if unicodedata.name(truc[0]) != 'SPACE':
            print(truc, unicodedata.name(truc[0]), t)


def attr_content_precedes(file_name, vol, string):
    out = ''
    tags = re.findall(r'<dw ([^>]+)>', string)
    for t in tags:
        if vol == '06':
            print(t)
        occurences = re.findall(t, string)
        if len(occurences) >= 2:
            out += 'ok '
        else:
            length = str(len(occurences[0])+10)
            regex = r'.{'+length+r'}'+t
            out += '\n'
            out += str(re.findall(regex, string))
            out += '\n'
    write_file('./processed/'+vol+'_tsawa_consistency.txt', out)

page_num = 1
def apply_formatting(file_name, vol, string):
    global page_num
    vol_names = {
        '01': 'གདུལ་ཞིང་སྣོད་བཅུད་ཀྱི་འཇིག་རྟེན་རིམ་པར་ཕྱེ་བ་སྟེ་གནས་དང་པོའི་འགྲེལ་པ',
        '02': 'སྟོན་པ་ཉིད་སྔོན་བྱང་ཆུབ་ཀྱི་ལམ་དུ་ཇི་ལྟར་གཤེགས་པའི་སྐབས།',
        '03': 'བསྟན་པ་དམ་པའི་ཆོས་ངོས་བཟུང་བའི་སྐབས།',
        '04': 'རྒྱལ་བསྟན་འཛམ་བུའི་གླིང་དུ་ཇི་ལྟར་དར་བའི་རིམ་པ་ཕྱེ་བ།',
        '05': 'ལྷག་པ་ཚུལ་ཁྲིམས་ཀྱི་བསླབ་པའི་རིམ་པར་ཕྱེ་བ་',
        '06': 'chapter 06',
        '07': 'chapter 07',
        '08': 'chapter 08',
        '09': 'chapter 09',
        '10': 'chapter 10'
    }
    num = vol.replace('.txt', '')
    heading = '<?xml version="1.0" encoding="UTF-8"?>\n'
    heading += '<document name="{}" vol="{}" tibetan="true">\n'.format(vol_names[num], num)

    formatted = re.sub(r'(<[a-z]+ )([^>]+)(>)', r'\1name="\2"\3', string)

    # segmenting into pages
    out = ''
    side = 'a'
    syls = 0
    in_tag = False
    out += '[{}]'.format(str(page_num) + side)
    for t in formatted:
        out += t

        # update wether in a tag or not
        if t == '<':
            in_tag = True
        if t == '>':
            in_tag = False

        # count syllables
        if not in_tag:
            if t == ' ' or t == '་':
                syls += 1

        # add the page number
        if syls == 350:
            if side == 'a':
                side = 'b'
                syls = 0
            else:
                side = 'a'
                page_num += 1
                syls = 0
            out += '\n[{}]'.format(str(page_num) + side)

    end = '</document>'

    write_file(xml_path+file_name+'.xml', heading+out+end)


def generate_dtd(file_name, vol, string):
    # initiate tags{}
    t = ['dw', 'tn', 'yw', 'dr', 'gd', 'l', 'pj', 'ds', 'ts', 'kd', 'ns']
    tags = {}
    for u in t:
        tags[u] = []

    # find all tags and values
    parts = re.findall(r'<([a-z]+) ([^>]+)>', string)
    # populate tags{}
    for p in parts:
        tag = p[0]
        value = p[1]
        tags[tag].append(value)

    # preparing the output file
    heading = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tags SYSTEM "struct/tags_template.dtd">\n'

    body = '<tags ref="{}.xml">\n'.format(file_name)
    for tag in sorted(tags.keys()):
        if tags[tag] == []:
            body += '\t<{}></{}>\n'.format(tag, tag)
        else:
            body += '\t<{}>\n'.format(tag)
            for t in tib_sort(tags[tag]):
                body += '\t\t<name>{}</name>\n'.format(t)
            body += '\t</{}>\n'.format(tag)
    body += '</tags>'

    write_file(tags_path+file_name+'_tags.xml', heading+body)




in_path = './raw_data/volumes'
xml_path = './processed/xml/'
tags_path = './processed/tags/'
for f in sorted(os.listdir(in_path)):
    print(f)
    number = re.sub(r'[a-z_]+([0-9]+).txt', r'\1', f)
    f_name = f.replace('.txt', '')

    content = open_file(in_path+'/'+f)
    if '< ' in content:
        print('ok')

    # find bad formatting
    #find_no_space_after_tag(content)

    # check wether the content of the attribute is the tsawa that precedes directly
    #attr_content_precedes(f.replace('.txt', ''), content)

    # put the string in the pseudo-tag within name=""
    apply_formatting(f_name, number, content)

    # generate dtd files (tags files)
    generate_dtd(f_name, number, content)

