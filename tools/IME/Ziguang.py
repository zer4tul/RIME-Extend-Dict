#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
from tools import *

class uwl(BaseDictFile):
    def __init__(self):
        BaseDictFile.__init__(self)
        self.hash = ''
        self.word_count = 0
        self.name = ''
        self.author = ''
        self.segment_count = 0
        self.segment_start = 0xc00
        self.segment_length = 0x400
        # 声母表
        self.shengmu = [ "", "b", "c", "ch", "d", "f", "g", "h", "j", "k", "l", "m", "n",
            "p", "q", "r", "s", "sh", "t", "w", "x", "y", "z", "zh"]
        # 韵母表
        self.yunmu = [ "ang", "a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er",
            "i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "o", "ong",
            "ou", "u", "ua", "uai", "uan", "uang", "ue", "ui", "un", "uo", "v"]
        # segment中每个词汇信息所占长度的映射表，不知道怎么想出来的
        self.len_code_dict = [0x05, 0x87, 0x09, 0x8B, 0x0D, 0x8F, 0x11, 0x13, 0x15, 0x17, 0x19]

    def get_dict_info(self, data):
        #typedef struct WORDLIBHEADER
        #{
        #	int			signature;							//词库的签名
        #	TCHAR		name[WORDLIB_NAME_LENGTH];			//词库的名称
        #	TCHAR		author_name[WORDLIB_AUTHOR_LENGTH];	//词库作者名称
        #	int			word_count;							//词汇数目
        #	int			page_count;							//已分配的页数
        #	int			can_be_edit;						//是否可以编辑
        #	int			pim_version;						//输入法版本号（兼容性考虑）
        #	int			index[CON_NUMBER][CON_NUMBER];		//索引表
        #}
        # 0~3字节是词库的hash值
        self.signature = struct.unpack('I', data[:4])
        # 4~35  字节：词库名
        # 36~67 字节：词库作者名
        self.name = byte2str(data[4:36]).rstrip('\x00')
        self.author = byte2str(data[36:68]).rstrip('\x00')
        # 68~71 字节：词汇数量
        # 72~75 字节：已分配的页面（page）数量
        # 76~89 字节：是否可写的标识位
        # 80~83 字节：输入法版本号
        # 剩下的3020字节不清楚是什么，有大量的空白
        self.word_count = struct.unpack('I',data[68:72])[0]
        self.segment_count = struct.unpack('I',data[72:76])[0]
        return self.name, self.author, self.word_count, self.segment_count

#    def _parse(self, data):
#        # 没搞懂这玩意是干嘛的
#        len_code_dict = [0x05, 0x87, 0x09, 0x8B, 0x0D, 0x8F, 0x11, 0x13, 0x15, 0x17, 0x19]
#        pos = 0
#        word = Word()
#        len_code = struct.unpack('B', data[pos])[0]
#        pos += 1
#        try:
#            length = len_code_dict.index(len_code) + 2
#        except ValueError:
#            print(repr(data))
#        len_byte = length * 4 + 4
#        # 计算词汇的权重，算法看起来很奇葩的样子
#        rank = struct.unpack('I', ''.join(struct.unpack('3c', data[pos:pos+3])) + '\x00')[0]
#        pos += 3
#        count = (rank - 1) / 32
#        # 计算拼音长度，最多允许8字节长度的拼音
#        if length <= 8:
#            pinyin_len = length
#        else:
#            pinyin_len = 8
#        pinyin = []
#        for i in xrange(pinyin_len):
#            # 计算声母编码
#            sm = struct.unpack('B', data[pos])[0]
#            sm_index = sm & 31
#            pos += 1
#            # 计算韵母编码
#            ym = struct.unpack('B', data[pos])[0]
#            ym_index = (sm >> 5) + (ym << 3)
#            pos += 1
#            # 从计算出来的拼音编码查询对应的拼音字母
#            try:
#                pinyin.append(self.shengmu[sm_index] + self.yunmu[ym_index])
#            except:
#                pass
#        word.pinyin = ' '.join(pinyin)
#
#        # 查询汉字
#        word.value = data[pos:pos+length*2]
#
#        return (word, len_byte)
#
#
#    def _parse_segment(self, data):
#        # Segment 单独取出来处理
#        pos = 0
#        # 0~3字节是索引编号（segment的编号，对应上面的segment_count），从0开始计数
#        # 4~7字节不知道是什么
#        # 8~11字节不知道是干嘛的，从深蓝的代码里抄的变量名
#        # 12~15字节是segment的实际内容长度
#        index_number, unknown, word_len_enums, word_byte_len = struct.unpack('4I', data[pos:pos+16])
#        print("-"*60)
#        print(repr(data))
#
#        # 开始读取segment中的有效内容，直到 length_read == word_byte_len
#        pos = 16
#        length_read = 0
#        while length_read < word_byte_len:
#            word, l = self._parse(data[pos:])
#            length_read += l
#            pos = pos + l
#            if self.dictionary.has_key(word.pinyin):
#                self.dictionary[word.pinyin].append(word)
#            else:
#                self.dictionary[word.pinyin] = []
#                self.dictionary[word.pinyin].append(word)

#    def _len_code(self, data):
#        read_byte = 0
#        valid = False
#        len_code = struct.unpack('B', data[read_byte])[0]
#        read_byte += 1

    def _len_code(self, data):
        read_byte = 0
        valid = False
        while not valid:
            len_code = struct.unpack('B', data[read_byte])[0]
            next_len_code = struct.unpack('B', data[read_byte+1])[0]
            read_byte += 1
            if (len_code in self.len_code_dict) and not (next_len_code in self.len_code_dict):
                valid = True
                break
            else:
                read_byte += 1
            #if read_byte >= len(data) or read_byte > length_limit:
            if read_byte >= len(data):
                    break
        if len_code not in self.len_code_dict:
            print('---------------------')
            print(repr(data))

        if len_code == 0 :
            length = None
            read_byte = len(data)
        else:
            length = self.len_code_dict.index(len_code) + 2
            length_limit = 1 + 3 + length * 4 + length * 4
            if length_limit >= len(data[read_byte:]):
                length = None
                read_byte = len(data)

        return (len_code, length, read_byte)

    def _parse(self, data):
        word = Word()
        len_code, length, read_byte = self._len_code(data)
        # 如果self._len_code 函数返回 None，表示剩余的数据中没有找到len_code，直接返回，不做解析
        if length == None:
            return(word, read_byte)
        len_byte = length * 4 + 4
        # 计算词汇的权重，算法看起来很奇葩的样子
        rank = struct.unpack('I', ''.join(struct.unpack('3c', data[read_byte:read_byte+3])) + '\x00')[0]
        read_byte += 3
        count = (rank - 1) / 32
        # 计算拼音长度，最多允许8字节长度的拼音
        if length <= 8:
            pinyin_len = length
        else:
            pinyin_len = 8
        pinyin = []
        for i in xrange(pinyin_len):
            # 计算声母编码
            try:
                sm = struct.unpack('B', data[read_byte])[0]
            except IndexError:
                print(repr(hex(len_code)), repr(data))
            sm_index = sm & 31
            read_byte += 1
            # 计算韵母编码
            ym = struct.unpack('B', data[read_byte])[0]
            ym_index = (sm >> 5) + (ym << 3)
            read_byte += 1
            # 从计算出来的拼音编码查询对应的拼音字母
            try:
                pinyin.append(self.shengmu[sm_index] + self.yunmu[ym_index])
            except:
                pass
        word.pinyin = ' '.join(pinyin)
        # debug: 计算最大长度
        #           len_code + rank + pinyin + hanzi
        # 查询汉字
        # TODO: 紫光uwl文件的解析有点问题，目前使用的解析规则并不能完全正确的解析出所有内容，所以需要验证获取到的词汇是否在汉字范围之内（包括ASCII英文）
        hanzi_len = length*2
        hanzi = byte2str(data[read_byte:read_byte+hanzi_len])
        read_byte += hanzi_len
        if is_cjk(hanzi):
            word.value = hanzi.encode('utf-8')

        #print('len_code: ' + repr(len_code) + '\t' + 'length/read_byte: ' + repr(length) + '/' + repr(read_byte) + '\t' + 'count: ' + repr(count) + '\t' + 'next_len_code: ' + '\t' + repr(next_len_code))
        #print(str(len(data[0:read_byte]))+ '\t' + repr(data[0:read_byte]) + '--->' + word.value + '\t' + ':' +'\t' + word.pinyin)
        return (word, read_byte)

    def _parse_segment(self, data):
        #typedef	struct PAGE
        #{
        #	int			page_no;							//页号
        #	int			next_page_no;						//下一个页号，-1标识结束
        #	int			length_flag;						//本页包含的词汇长度的标志
        #	int			data_length;						//已经使用的数据长度
        #	char		data[WORDLIB_PAGE_DATA_LENGTH];		//数据开始
        #} PAGE;
        # Segment 单独取出来处理
        pos = 0
        # 0~3字节是索引编号（segment的编号，对应上面的segment_count），从0开始计数
        # 4~7字节不知道是什么
        # 8~11字节不知道是干嘛的，从深蓝的代码里抄的变量名
        # 12~15字节是segment的实际内容长度
        index_number, unknown, word_len_enums, word_byte_len = struct.unpack('4I', data[pos:pos+16])
        #print("-"*60)
        #print(repr(data))

        # 开始读取segment中的有效内容，直到 length_read == word_byte_len
        pos = 16
        length_read = 0
        while length_read < word_byte_len:
            word, l = self._parse(data[pos:])
            length_read += l
            pos = pos + l
            if word.value:
                if self.dictionary.has_key(word.pinyin):
                    self.dictionary[word.pinyin].append(word)
                else:
                    self.dictionary[word.pinyin] = []
                    self.dictionary[word.pinyin].append(word)
        return self.dictionary

    def load(self, filename):
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        return self.read(data)

    def read(self, data):
        self.get_dict_info(data)
        for i in xrange(self.segment_count):
            # debug
#            print('segment: ' + str(i))
            pos = self.segment_start + self.segment_length * i
            self._parse_segment(data[pos:pos+self.segment_length])
#            try:
#                self._parse_segment(data[pos:pos+self.segment_length])
#            except ValueError, e:
#                print(repr(data[pos:pos+self.segment_length]))
#                raise Exception(e)
        return self.dictionary
