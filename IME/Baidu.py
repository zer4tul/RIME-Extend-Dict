#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from tools import *


class bdict(BaseDictFile):
    def __init__(self):
        BaseDictFile.__init__(self)
        # 文件头
        self.head = 'biptbdsw'
        # 文件终点偏移
        self.offset = 0x60
        self.end_position = 0
        # 词表偏移
        self.dict_start = 0x350
        self.shengmu = [ "c", "d", "b", "f", "g", "h", "ch", "j", "k", "l", "m", "n", "", "p", "q", "r", "s", "t", "sh", "zh", "w", "x", "y", "z"]
        self.yunmu = [ "uang", "iang", "iong", "ang", "eng", "ian", "iao", "ing", "ong", "uai", "uan", "ai", "an", "ao", "ei", "en", "er", "ua", "ie", "in", "iu", "ou", "ia", "ue", "ui", "un", "uo", "a", "e", "i", "o", "u", "v"]

    def _get_word_len(self, data, pos = 0):
        # 单词长度
        length = struct.unpack('I', data[pos:pos+4])[0]
        #print(repr(data[pos:pos+length*3+1]))
        return length

    def _get_word(self, data, length = 0):
        pos = 0
        word = Word()
        pinyin = []
        for i in xrange(length):
            tmp = struct.unpack('2B', data[pos:pos+2])
            pos = pos + 2
            sm = tmp[0]
            ym = tmp[1]
            pinyin.append(self.shengmu[sm] + self.yunmu[ym])
#            try:
#                pinyin.append(self.shengmu[sm] + self.yunmu[ym])
#            except IndexError:
#                print(repr(data))
        word.pinyin = ' '.join(pinyin)
        hanzi = byte2str(data[pos:pos+ length*2])
        pos = pos+ length*2
        word.value = hanzi.encode('utf-8')
#        print(word)
        return word

    def get_dict_info(self, data):
        self.end_position = struct.unpack('I', data[self.offset:self.offset+4])[0]


    def load(self, filename):
        f = open(filename,'rb')
        data = f.read()
        f.close()

        if data[0:8] != self.head:
            print "It's not a bdict file"
            sys.exit(1)

        return self.read(data)

    def read(self, data):
        self.get_dict_info(data)

        pos = self.dict_start
        while pos < self.end_position:
#            print(pos, self.end_position)
#            if pos >= self.end_position:
#                break
            # 这里的长度是算字数的，实际长度是 拼音数(length * 2) + 字符长度(length * 2)
            length = self._get_word_len(data, pos = pos)
            pos += 4
            #print('*'*60)
            #print(repr(data[pos:pos+length*4]))
            word = self._get_word(data[pos:pos+length*4], length = length)
            pos = pos + length * 4
            if word.value:
                if self.dictionary.has_key(word.pinyin):
                    self.dictionary[word.pinyin].append(word)
                else:
                    self.dictionary[word.pinyin] = []
                    self.dictionary[word.pinyin].append(word)

        return self.dictionary
