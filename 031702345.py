# -*- coding: utf-8 -*-
#encoding:utf-8
# this is from PEP 263

import json
import cpca
import numpy
import requests
import re
#import jieba
#jieba is included in cpca
#chinese_province_city_area_mapper https://github.com/DQinYuan/chinese_province_city_area_mapper

try :
    threeleveljson = open('threelevel.json', 'r', encoding='utf-8')
    threeleveldict = json.load(threeleveljson)
    threeleveljson.close()
    town = open('town.txt', 'r', encoding='utf-8')
    towns=town.readlines()
    town.close()
except Exception as e:
    print("Cannot open threelevel.json or town.txt",e)

# print to json
def printTojson1(name,tel,address):
    ans={}
    ans['姓名']=name
    ans['手机']=tel
    ans['地址']=address
    jsonarray = json.dumps(ans, ensure_ascii=False)
    print(jsonarray)
    return

def threeAddress(rawaddress):
    address = numpy.array(cpca.transform([rawaddress], umap={}))[0]
    return [address[0],address[1],address[2],address[3]]

def fourthAddress(rawaddress):
    findss=['']
    for line in towns:
        sss=line[:-1]
        if re.match(sss,rawaddress) != None:
            findss=re.split(sss,rawaddress,maxsplit=1)
            findss[0]=sss
            return findss
    findss.append(rawaddress)
    return findss

def fivethAddress(rawaddress):
    ans=['','']
    addr = re.match(r".*(路|街|胡同|道|里|巷)", rawaddress)
    if addr:
        ans[0] = addr.group(0)
        ans[1] = re.sub(r".*(路|街|胡同|道|里|巷)", '', rawaddress)
    else:
        ans[1] = rawaddress
    return ans

def sixthAddress(rawaddress):
    ans = ['', '']
    addr = re.match(r".*(号|弄)", rawaddress)
    if addr:
        ans[0] = addr.group(0)
        ans[1] = re.sub(r".*(号|弄)", '', rawaddress)
    else:
        ans[1] = rawaddress
    return ans

def addressTransfr(address0):
    if(address0=='北京市' or address0=='上海市' or  address0=='天津市' or address0=='重庆市'):
        return  address0[:2]
    else:
        return  address0
def diffMode1(rawaddress):
    address = numpy.array(cpca.transform([rawaddress], cut=False,umap={"徐州市":"徐州经济技术开发区"},pos_sensitive=True))[0]
    if address[4] == -1:
        address[0] = ''
    if address[5] == -1:
        address[1] = ''
    if address[6] == -1:
        address[2] = ''
    address[0]=addressTransfr(address[0])
    addr4=fourthAddress(address[3])
    return [address[0], address[1], address[2], addr4[0],addr4[1]]

def diffMode2(rawaddress):
    mixaddress=diffMode1(rawaddress)
    addr5=fivethAddress(mixaddress[4])
    mixaddress[4]=addr5[0]
    addr6=sixthAddress(addr5[1])
    mixaddress.append(addr6[0])
    mixaddress.append(addr6[1])
    return mixaddress

def diffMode3(rawaddress):
    my_key = '4217b885adb16e0541338722c26beded'
    parameters_1 = {'key': my_key, 'address': rawaddress}
    url_1 = 'https://restapi.amap.com/v3/geocode/geo?parameters'
    ret_1 = requests.get(url_1, parameters_1).json()
    location = ret_1['geocodes'][0]['location']
    parameters_2 = {'key': my_key, 'location': location}
    url_2 = 'https://restapi.amap.com/v3/geocode/regeo?parameters'
    ret_2 = requests.get(url_2, parameters_2).json()
    mapaddress=ret_2['regeocode']['formatted_address']
    addressthree=diffMode2(mapaddress)
    rawaddress=rawaddress.split('号')
    if len(rawaddress) >1:
        addressthree[6]=rawaddress[1]
    return addressthree

def main(rawaddress):# rawInputFromConsole():
    mode = 0# runmode: default is 1
    modestring = rawaddress[:2]
    if  modestring == "1!":
        mode=1
        rawaddress = rawaddress[2:]
    elif modestring == "2!":
        mode=2
        rawaddress = rawaddress[2:]
    elif modestring == "3!":
        mode=3
        rawaddress = rawaddress[2:]
    # split name from raw by ","
    rawaddress = rawaddress.split(",")
    name = rawaddress[0]
    mixaddress = rawaddress[1]
    # get phone number from mixaddress
    number = ""
    numberfind = False
    numberlength = 11
    thislength = 0
    thispos = -1
    i = 0
    for x in mixaddress:
        if(x.isdigit()==True):
            number = number + x
            thispos = i
            thislength = thislength +1
            if(thislength == numberlength ) :
                numberfind =True
                break
        else:
            number = ""
            thislength = 0
        i = i + 1
    if numberfind == False:
        number = ""
    address = mixaddress[:thispos-(numberlength-1)]+mixaddress[thispos+1:]
    # remove . in the end
    address = address.split(".")[0]
    if mode == 1 or mode == 0:
        address = diffMode1(address)
    elif mode == 2:
        address = diffMode2(address)
    else:
        address = diffMode3(address)
    printTojson1(name,number,address)

while 1:
    try:
        inputraw=input();
        if(inputraw=="END"):
            break
    except Exception as e:
        print("Input ERROR")
    main(inputraw)
'''''''''
    #街道 镇 乡 地区 产业基地 开发区
    addr4 = rawaddress.split('镇', 1)
    if len(addr4) > 1:
        addr4[0] += "镇"
    else:
        addr4 = rawaddress.split('街道', 1)
        if len(addr4) > 1:
            addr4[0] += "街道"
        else:
            addr4 = rawaddress.split('乡', 1)
            if len(addr4) > 1:
                addr4[0] += "乡"
            else:
                addr4 = rawaddress.split('地区', 1)
                if len(addr4) > 1:
                    addr4[0] += "地区"
                else:
                    addr4 = rawaddress.split('产业基地', 1)
                    if len(addr4) > 1:
                        addr4[0] += "产业基地"
                    else:
                        addr4 = rawaddress.split('开发区', 1)
                        if len(addr4) > 1:
                            addr4[0] += "开发区"
                        else:
                            addr4.insert(0, '')
    return addr4
'''''''''
