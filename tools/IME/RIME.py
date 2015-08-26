#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from tools import *
import datetime


class luna_pinyin(BaseDictFile):
    def __init__(self):
        BaseDictFile.__init__(self)
        # 文件头
        self.head = '''# Rime dictionary
        # encoding: utf-8
        #
        # 「Rime词库扩展计划」——为RIME打造一个强大好用的词库
        ---
        name: luna_pinyin.extend
        version: "%s"
        sort: by_weight
        use_preset_vocabulary: true
        ...''' % (datetime.datetime.today().strftime('%Y%m%d'))

    def load(self, filename):
        f = open(filename,'r')
        data = f.read()
        f.close()

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
