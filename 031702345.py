# -*- coding: utf-8 -*-
#encoding:utf-8
# this is from PEP 263

import json
import cpca
import numpy
import requests
#import jieba
#jieba is included in cpca
#chinese_province_city_area_mapper https://github.com/DQinYuan/chinese_province_city_area_mapper
#刘六,福州市南屿镇五峰里1号福州旗山森林国家旅游区
#王一,上海市浦东新区锦13101111111绣路1001号世纪公园

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
    address = [rawaddress]
    address = cpca.transform(address, umap={})
    address = numpy.array(address)
    address = address[0]
    ans = [address[0],address[1],address[2],address[3]]
    return ans

def fourthAddress(rawaddress):
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

def fivethAddress(rawaddress):
    #路 街
    addr5 = rawaddress.split('路', 1)
    if len(addr5) > 1:
        addr5[0] += "路"
    else:
        addr5 = rawaddress.split('街', 1)
        if len(addr5) > 1:
            addr5[0] += "街"
        else:
            addr5.insert(0, '')
    return addr5

def sixthAddress(rawaddress):
    #号
    addr6 = rawaddress.split('号', 1)
    if len(addr6) > 1:
        addr6[0] += "号"
    else:
        addr6.insert(0, '')
    return addr6

def addressTransfr(address0):
    if(address0=='北京市' or address0=='上海市' or  address0=='天津市' or address0=='重庆市'):
        return  address0[:2]
    else:
        return  address0
def diffMode1(rawaddress):
    address = [rawaddress]
    address = cpca.transform(address, cut=False,umap={"徐州市":"徐州经济技术开发区"},pos_sensitive=True)
    address = numpy.array(address)
    address = address[0]
    if address[4] == -1:
        address[0] = ''
    if address[5] == -1:
        address[1] = ''
    if address[6] == -1:
        address[2] = ''
    address[0]=addressTransfr(address[0])
    addr4=fourthAddress(address[3])
    #print(addr4)
    #rawaddress=jieba.lcut(address[3])
    #print(rawaddress)
    ans = [address[0], address[1], address[2], addr4[0],addr4[1]]
    return ans

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

def main(rawaddress):
    # rawInputFromConsole():
    # runmode: default is 1
    mode = 0
    modestring = rawaddress[:1]
    if  modestring == "1":
        mode=1
        rawaddress = rawaddress[2:]
    elif modestring == "2":
        mode=2
        rawaddress = rawaddress[2:]
    elif modestring == "3":
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
    if numberfind == True:
        donothing = 1
        #debug:print("success get phone number:")
        #debug:print(number)
    else:
        #debug:print("cannot get phone number")
        number = ""
    address = mixaddress[:thispos-(numberlength-1)]+mixaddress[thispos+1:]
    # remove . in the end
    address = address.split(".")
    address = address[0]
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
    except EOFError:
        break
    main(inputraw)
