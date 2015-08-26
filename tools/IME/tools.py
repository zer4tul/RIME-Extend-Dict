#!/usr/bin/env python
# -*- coding: utf-8 -*-


def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def get_locale():
    import locale
    if locale.getlocale()[1]:
        return locale.getlocale()[1]
    else:
        return locale.getdefaultlocale()[1]


def is_cjk (strings):
    from string import printable
    valid = False
    ascii_range = {
        'ASCII'                        : [u'\x00',u'\x7f']
    }
    cjk_range = {
        'CJK Unified Ideographs block' : [u'\u4E00',u'\u9FCC'],
        'CJKUI Ext A block'            : [u'\u3400',u'\u4DB5'],
        'CJKUI Ext B block'            : [u'\u20000',u'\u2A6D6'],
        'CJKUI Ext C block'            : [u'\u2A700',u'\u2B734'],
        'CJKUI Ext D block'            : [u'\u2B740',u'\u2B81D']
    }
    if type(strings) != type(unicode()):
        strings = unicode(strings, 'utf-8')
    for i in strings:
        valid = False
        for j in cjk_range.keys():
            if i >= cjk_range[j][0] and i <= cjk_range[j][1]:
                #print(i.encode('utf-8'), cjk_range[j])
                valid = True
            elif i in printable:
                valid = True
        if not valid:
            return valid
    return valid

def byte2str(data):
    '''将原始字节码转为字符串'''
    import struct
    i = 0;
    length = len(data)
    ret = u''
    while i < length:
        x = data[i] + data[i+1]
        t = unichr(struct.unpack('H',x)[0])
        if t == u'\r':
            ret += u'\n'
        elif t != u' ':
            ret += t
        i += 2
    return ret

class Word(object):
    def __init__(self, value='', encoding='utf-8', count=0):
        self.value = value
        self.count = count
        self.pinyin = None
        self.encoding = encoding
    def __repr__(self):
        return self.value

class WordDict(dict):
    def _opencc(self, string):
        """Call opencc command line tool to translate characters"""
        import subprocess
        opencc_exec = which('opencc')
        if not opencc_exec:
            raise Exception('opencc command line tool could not found in $PATH')
        p = subprocess.Popen([opencc_exec], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        result, error = p.communicate(string)
#        result = subprocess.check_output([opencc_exec, '-i', filename], shell=False)
        return result.rstrip()

    def zhs_to_zht(self):
        """Translate characters from Simplified Chinese into Traditional Chinese"""
        #from tempfile import NamedTemporaryFile
        #tempfile = NamedTemporaryFile(mode='rw', bufsize=0)
        tmp_string = ''
        for key in self.keys():
            w = []
            for i in xrange(len(self[key])):
                w.append(self[key][i].value)
            tmp_string += key + ':' + '\t'.join(w)+'\n'
        #    tempfile.write(line)
        tmp_string = self._opencc(tmp_string)
        print(tmp_string)
        for line in tmp_string.split('\n'):
            key, words = line.split(':', 1)
            words = words.split('\t')
            for i in xrange(len(self[key])):
                self[key][i].value = words[i]
#            self[key] = map(self._opencc, self[key])
#            for i in xrange(len(self[key])):
#                self[key][i].value = self._opencc(self[key][i].value)

    def word(self, key):
        result = []
        for w in self[key]:
            result.append(w.value)
        return result

    def dump(self, filename, order = 'pinyin'):
        f = open(filename, 'w')
        self.zhs_to_zht()
        key = self.keys()
        key.sort()
        for k in key:
            line = '\n'.join(self.word(k))+'\n'
            f.write(line)
        f.close()

class BaseDictFile(object):
    def __init__(self):
        self.pinyin_table = {}
        self.dictionary = WordDict()
        self.magic_number = ''
        self.offset = 0
