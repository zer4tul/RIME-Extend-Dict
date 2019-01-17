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
        char = struct.unpack('B', data[pos+4])[0]
        pure_english = False
        if 0x41 <= char <= 0x7a:
            pure_english = True
        #print(repr(data[pos:pos+length*3+1]))
        return (length, pure_english)

    def _get_word(self, data, length = 0, pure_english = False):
        pos = 0
        word = Word()
        pinyin = []
        for i in xrange(length):
            char = struct.unpack('B', data[pos])[0]
            pos += 1
            if pure_english:
                # 如果读取到的首个hex值落在字母区域（0x41 ~ 0x7a）内，说明是纯英文，后面的内容直接读取即可
                pinyin.append(chr(char).lower())
                word.value += chr(char)
            else:
                if char == 0xff:
                    # 声母部分如果是'\xff'，说明这是中英文混输的英文字母，不需要做拼音词表转换，直接读取韵母部分即可
                    sm = ''
                    ym = struct.unpack('c', data[pos])[0]
                    pos += 1
                    pinyin.append('' + ym)
                else:
                    sm = char
                    ym = struct.unpack('B', data[pos])[0]
                    pos += 1
                    pinyin.append(self.shengmu[sm] + self.yunmu[ym])
#                    try:
#                        pinyin.append(self.shengmu[sm] + self.yunmu[ym])
#                    except IndexError:
#                        print(repr(data))
#                        raise IndexError
        if pure_english:
            word.pinyin = ' '.join(pinyin)
        else:
            word.pinyin = ' '.join(pinyin)
            hanzi = byte2str(data[pos:pos+ length*2])
            hanzi = hanzi.strip('\x00')
            pos = pos+ length*2
            word.value = hanzi.encode('utf-8')
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
            length, pure_english = self._get_word_len(data, pos = pos)
            pos += 4
            #print('*'*60)
            #print(repr(data[pos:pos+length*4]))
            if pure_english:
                word = self._get_word(data[pos:pos+length], length = length, pure_english = True)
                pos = pos + length
            else:
                word = self._get_word(data[pos:pos+length*4], length = length)
                pos = pos + length * 4
            if word.value:
                if self.dictionary.has_key(word.pinyin):
                    # 校验拼音和词汇的长度是否相等，如不相等则丢弃
                    if len(word.value.decode('utf-8')) == len(word.pinyin.split(' ')):
                        self.dictionary[word.pinyin].append(word)
        #                print(word.value.decode('utf-8'), len(word.value.decode('utf-8')), word.pinyin,len(word.pinyin.split(' ')))
                    #if word.value.decocde('utf-8') == u'\u7fbd\u5b50':
#                        print(word.dump())
                else:
                    if len(word.value.decode('utf-8')) == len(word.pinyin.split(' ')):
                        self.dictionary[word.pinyin] = []
                        self.dictionary[word.pinyin].append(word)
#                        print(word.dump())

        return self.dictionary
