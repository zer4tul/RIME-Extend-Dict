#!/usr/bin/python
# -*- coding: utf-8 -*-


import struct
import sys
import binascii
import pdb
import os
from IME import *

from tempfile import NamedTemporaryFile



if __name__ == '__main__':

    #将要转换的词库添加在这里就可以了
    FILES = sys.argv[1:]
    
    for f in FILES:
        filename, fileext = os.path.splitext(os.path.basename(f))
        if fileext.lower() == '.scel':
            worddict = Sougou.scel()
        elif fileext.lower() == '.uwl':
            worddict = Ziguang.uwl()
        elif fileext.lower() == '.bdict':
            worddict = Baidu.bdict()

        # 获取文件名
        OUTPUT = filename + ".txt"
        d = worddict.load(f)
        d.dump(OUTPUT)
        #保存结果
        #f = open(OUTPUT,'w')
        
#    #保存结果
#    f = open('sougou.txt','w')
#    for count,py,word in GTable:
#        #GTable保存着结果，是一个列表，每个元素是一个元组(词频,拼音,中文词组)，有需要的话可以保存成自己需要个格式
#        #我没排序，所以结果是按照上面输入文件的顺序
#        f.write( unicode('{%(count)s}' %{'count':count}+py+' '+ word).encode('GB18030') )#最终保存文件的编码，可以自给改
#        f.write('\n')
#    f.close()    
