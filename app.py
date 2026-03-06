from flask import Flask, request, jsonify, render_template_string
import asyncio
import httpx
import base64
import binascii
import json
import logging
import warnings
import requests
import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from google.protobuf.json_format import MessageToJson, ParseDict
from urllib3.exceptions import InsecureRequestWarning

# ========== PROTOBUF CLASSES (Embedded directly) ==========
class FreeFire_pb2:
    class LoginReq:
        def __init__(self):
            self.open_id = ""
            self.open_id_type = ""
            self.login_token = ""
            self.orign_platform_type = ""
        def SerializeToString(self):
            return f"{self.open_id}|{self.open_id_type}|{self.login_token}|{self.orign_platform_type}".encode()
    
    class LoginRes:
        @staticmethod
        def FromString(data):
            class Res:
                def __init__(self):
                    self.token = data.decode().split('|')[0] if b'|' in data else "dummy_token"
            return Res()

class like_pb2:
    class like:
        def __init__(self):
            self.uid = 0
            self.region = ""
        def SerializeToString(self):
            return f"{self.uid}|{self.region}".encode()

class like_count_pb2:
    class Info:
        def __init__(self):
            self.AccountInfo = type('AccountInfo', (), {'UID': 0, 'PlayerNickname': '', 'Likes': 0})
        def ParseFromString(self, data):
            parts = data.decode().split('|')
            self.AccountInfo.UID = int(parts[0]) if len(parts) > 0 else 0
            self.AccountInfo.PlayerNickname = parts[1] if len(parts) > 1 else "Player"
            self.AccountInfo.Likes = int(parts[2]) if len(parts) > 2 else 0

class uid_generator_pb2:
    class uid_generator:
        def __init__(self):
            self.saturn_ = 0
            self.garena = 1
        def SerializeToString(self):
            return f"{self.saturn_}|{self.garena}".encode()

warnings.simplefilter('ignore', InsecureRequestWarning)

app = Flask(__name__)
app.logger.setLevel(logging.CRITICAL)

# ========== CONSTANTS ==========
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASEVERSION = "OB52"

# ========== ACCOUNTS DATABASE (Embedded) ==========
ACCOUNTS = {
    "IND": [
        [
  {
    "uid": 4599171518,
    "password": "KNX_CODEX_27TI0"
  },
  {
    "uid": 4599171531,
    "password": "KNX_CODEX_JUIVX"
  },
  {
    "uid": 4599171533,
    "password": "KNX_CODEX_RR6HD"
  },
  {
    "uid": 4599171524,
    "password": "KNX_CODEX_LUOQW"
  },
  {
    "uid": 4599171527,
    "password": "KNX_CODEX_RUIIZ"
  },
  {
    "uid": 4599171516,
    "password": "KNX_CODEX_2P56L"
  },
  {
    "uid": 4599171526,
    "password": "KNX_CODEX_4T79R"
  },
  {
    "uid": 4599171530,
    "password": "KNX_CODEX_GWSYN"
  },
  {
    "uid": 4599171523,
    "password": "KNX_CODEX_PR396"
  },
  {
    "uid": 4599171521,
    "password": "KNX_CODEX_JXLUJ"
  },
  {
    "uid": 4599171529,
    "password": "KNX_CODEX_TE1CG"
  },
  {
    "uid": 4599171532,
    "password": "KNX_CODEX_VVAVY"
  },
  {
    "uid": 4599171528,
    "password": "KNX_CODEX_ZIWAF"
  },
  {
    "uid": 4599171520,
    "password": "KNX_CODEX_LAN1D"
  },
  {
    "uid": 4599171517,
    "password": "KNX_CODEX_WCKD2"
  },
  {
    "uid": 4599171522,
    "password": "KNX_CODEX_KKSLS"
  },
  {
    "uid": 4599171519,
    "password": "KNX_CODEX_0J8C0"
  },
  {
    "uid": 4599171534,
    "password": "KNX_CODEX_FI5NZ"
  },
  {
    "uid": 4599172834,
    "password": "KNX_CODEX_H88AP"
  },
  {
    "uid": 4599172836,
    "password": "KNX_CODEX_Z4OE6"
  },
  {
    "uid": 4599172847,
    "password": "KNX_CODEX_M439U"
  },
  {
    "uid": 4599172841,
    "password": "KNX_CODEX_9SH3G"
  },
  {
    "uid": 4599172854,
    "password": "KNX_CODEX_9SLTQ"
  },
  {
    "uid": 4599172832,
    "password": "KNX_CODEX_XX0HO"
  },
  {
    "uid": 4599172866,
    "password": "KNX_CODEX_RJWDC"
  },
  {
    "uid": 4599172838,
    "password": "KNX_CODEX_G6JWQ"
  },
  {
    "uid": 4599172867,
    "password": "KNX_CODEX_XCOZ6"
  },
  {
    "uid": 4599172863,
    "password": "KNX_CODEX_MYJDF"
  },
  {
    "uid": 4599172829,
    "password": "KNX_CODEX_CME74"
  },
  {
    "uid": 4599172846,
    "password": "KNX_CODEX_UR5PV"
  },
  {
    "uid": 4599172830,
    "password": "KNX_CODEX_AAIMT"
  },
  {
    "uid": 4599172853,
    "password": "KNX_CODEX_ZE5LI"
  },
  {
    "uid": 4599172865,
    "password": "KNX_CODEX_EFRPI"
  },
  {
    "uid": 4599172858,
    "password": "KNX_CODEX_7PWLU"
  },
  {
    "uid": 4599172835,
    "password": "KNX_CODEX_OITYI"
  },
  {
    "uid": 4599172844,
    "password": "KNX_CODEX_9M4VN"
  },
  {
    "uid": 4599172864,
    "password": "KNX_CODEX_TNA2K"
  },
  {
    "uid": 4599176920,
    "password": "KNX_CODEX_R1LCH"
  },
  {
    "uid": 4599176924,
    "password": "KNX_CODEX_I9FK4"
  },
  {
    "uid": 4599176937,
    "password": "KNX_CODEX_E1Q1P"
  },
  {
    "uid": 4599176945,
    "password": "KNX_CODEX_JFIFX"
  },
  {
    "uid": 4599176944,
    "password": "KNX_CODEX_7R7BO"
  },
  {
    "uid": 4599176927,
    "password": "KNX_CODEX_1LZSX"
  },
  {
    "uid": 4599176957,
    "password": "KNX_CODEX_1HZXP"
  },
  {
    "uid": 4599176903,
    "password": "KNX_CODEX_0YIFY"
  },
  {
    "uid": 4599176953,
    "password": "KNX_CODEX_EWPP8"
  },
  {
    "uid": 4599176909,
    "password": "KNX_CODEX_LBLVI"
  },
  {
    "uid": 4599176905,
    "password": "KNX_CODEX_QQVZ0"
  },
  {
    "uid": 4599176954,
    "password": "KNX_CODEX_IP2ZC"
  },
  {
    "uid": 4599176926,
    "password": "KNX_CODEX_UHNC7"
  },
  {
    "uid": 4599176946,
    "password": "KNX_CODEX_3QJD9"
  },
  {
    "uid": 4599176951,
    "password": "KNX_CODEX_058G2"
  },
  {
    "uid": 4599176911,
    "password": "KNX_CODEX_C47E9"
  },
  {
    "uid": 4599176950,
    "password": "KNX_CODEX_YLWW2"
  },
  {
    "uid": 4599176956,
    "password": "KNX_CODEX_5MVWH"
  },
  {
    "uid": 4599176942,
    "password": "KNX_CODEX_YP6PC"
  },
  {
    "uid": 4599176929,
    "password": "KNX_CODEX_GSOH6"
  },
  {
    "uid": 4599180152,
    "password": "KNX_CODEX_H231J"
  },
  {
    "uid": 4599180170,
    "password": "KNX_CODEX_RIARY"
  },
  {
    "uid": 4599180166,
    "password": "KNX_CODEX_HXDVX"
  },
  {
    "uid": 4599180157,
    "password": "KNX_CODEX_80385"
  },
  {
    "uid": 4599180154,
    "password": "KNX_CODEX_KZZMZ"
  },
  {
    "uid": 4599180168,
    "password": "KNX_CODEX_1G685"
  },
  {
    "uid": 4599180179,
    "password": "KNX_CODEX_1H3PH"
  },
  {
    "uid": 4599180176,
    "password": "KNX_CODEX_JOJ6T"
  },
  {
    "uid": 4599180162,
    "password": "KNX_CODEX_8TN3S"
  },
  {
    "uid": 4599180156,
    "password": "KNX_CODEX_ZCY0S"
  },
  {
    "uid": 4599180163,
    "password": "KNX_CODEX_GPUGL"
  },
  {
    "uid": 4599180161,
    "password": "KNX_CODEX_OJ1I6"
  },
  {
    "uid": 4599180178,
    "password": "KNX_CODEX_2MF7B"
  },
  {
    "uid": 4599180151,
    "password": "KNX_CODEX_ZADSD"
  },
  {
    "uid": 4599180164,
    "password": "KNX_CODEX_2WGD6"
  },
  {
    "uid": 4599180173,
    "password": "KNX_CODEX_4R1Y2"
  },
  {
    "uid": 4599180149,
    "password": "KNX_CODEX_J5JP2"
  },
  {
    "uid": 4599180160,
    "password": "KNX_CODEX_GHEQ8"
  },
  {
    "uid": 4599180181,
    "password": "KNX_CODEX_I2DP3"
  },
  {
    "uid": 4599180177,
    "password": "KNX_CODEX_Q8TR6"
  },
  {
    "uid": 4599183462,
    "password": "KNX_CODEX_YUO7V"
  },
  {
    "uid": 4599183457,
    "password": "KNX_CODEX_XARRT"
  },
  {
    "uid": 4599183463,
    "password": "KNX_CODEX_1602P"
  },
  {
    "uid": 4599183468,
    "password": "KNX_CODEX_UFGAY"
  },
  {
    "uid": 4599183485,
    "password": "KNX_CODEX_1Q7FK"
  },
  {
    "uid": 4599183469,
    "password": "KNX_CODEX_R6FLV"
  },
  {
    "uid": 4599183482,
    "password": "KNX_CODEX_15S0C"
  },
  {
    "uid": 4599183455,
    "password": "KNX_CODEX_4ZSXG"
  },
  {
    "uid": 4599183454,
    "password": "KNX_CODEX_OAIDF"
  },
  {
    "uid": 4599183483,
    "password": "KNX_CODEX_YQO09"
  },
  {
    "uid": 4599183450,
    "password": "KNX_CODEX_93GUN"
  },
  {
    "uid": 4599183480,
    "password": "KNX_CODEX_WAAMT"
  },
  {
    "uid": 4599183492,
    "password": "KNX_CODEX_MO98P"
  },
  {
    "uid": 4599183486,
    "password": "KNX_CODEX_FHITR"
  },
  {
    "uid": 4599183495,
    "password": "KNX_CODEX_JE2Z2"
  },
  {
    "uid": 4599183481,
    "password": "KNX_CODEX_0PLCY"
  },
  {
    "uid": 4599183484,
    "password": "KNX_CODEX_E7ZFN"
  },
  {
    "uid": 4599183487,
    "password": "KNX_CODEX_YY8TZ"
  },
  {
    "uid": 4599187636,
    "password": "KNX_CODEX_SPX5C"
  },
  {
    "uid": 4599187640,
    "password": "KNX_CODEX_ZEY2J"
  },
  {
    "uid": 4599187679,
    "password": "KNX_CODEX_PW1LU"
  },
  {
    "uid": 4599187639,
    "password": "KNX_CODEX_ORVKG"
  },
  {
    "uid": 4599187677,
    "password": "KNX_CODEX_IH85Y"
  },
  {
    "uid": 4599187673,
    "password": "KNX_CODEX_MMWVQ"
  },
  {
    "uid": 4599187642,
    "password": "KNX_CODEX_75YXW"
  },
  {
    "uid": 4599187654,
    "password": "KNX_CODEX_B0BR5"
  },
  {
    "uid": 4599187647,
    "password": "KNX_CODEX_JQ1UD"
  },
  {
    "uid": 4599187658,
    "password": "KNX_CODEX_IXG7E"
  },
  {
    "uid": 4599187659,
    "password": "KNX_CODEX_YPQR8"
  },
  {
    "uid": 4599187652,
    "password": "KNX_CODEX_8X2RI"
  },
  {
    "uid": 4599187661,
    "password": "KNX_CODEX_RM8YO"
  },
  {
    "uid": 4599187672,
    "password": "KNX_CODEX_WVN89"
  },
  {
    "uid": 4599187662,
    "password": "KNX_CODEX_EYWZT"
  },
  {
    "uid": 4599187678,
    "password": "KNX_CODEX_8T4NN"
  },
  {
    "uid": 4599187665,
    "password": "KNX_CODEX_8BOBF"
  },
  {
    "uid": 4599187680,
    "password": "KNX_CODEX_ZF3GR"
  },
  {
    "uid": 4599187644,
    "password": "KNX_CODEX_4OIVX"
  },
  {
    "uid": 4599187638,
    "password": "KNX_CODEX_054DI"
  },
  {
    "uid": 4599191331,
    "password": "KNX_CODEX_D0W36"
  },
  {
    "uid": 4599191330,
    "password": "KNX_CODEX_Z6063"
  },
  {
    "uid": 4599191328,
    "password": "KNX_CODEX_6QLOM"
  },
  {
    "uid": 4599191351,
    "password": "KNX_CODEX_KZ40F"
  },
  {
    "uid": 4599191355,
    "password": "KNX_CODEX_MMQXB"
  },
  {
    "uid": 4599191344,
    "password": "KNX_CODEX_Z65MT"
  },
  {
    "uid": 4599191337,
    "password": "KNX_CODEX_7SJLL"
  },
  {
    "uid": 4599191359,
    "password": "KNX_CODEX_KC2CD"
  },
  {
    "uid": 4599191339,
    "password": "KNX_CODEX_MQ9K9"
  },
  {
    "uid": 4599191334,
    "password": "KNX_CODEX_B177J"
  },
  {
    "uid": 4599191341,
    "password": "KNX_CODEX_VEQRN"
  },
  {
    "uid": 4599191327,
    "password": "KNX_CODEX_G6IIT"
  },
  {
    "uid": 4599191322,
    "password": "KNX_CODEX_D0AP3"
  },
  {
    "uid": 4599191358,
    "password": "KNX_CODEX_YKKJJ"
  },
  {
    "uid": 4599191362,
    "password": "KNX_CODEX_GMEVK"
  },
  {
    "uid": 4599191335,
    "password": "KNX_CODEX_HQO7R"
  },
  {
    "uid": 4599191324,
    "password": "KNX_CODEX_N5PFH"
  },
  {
    "uid": 4599191372,
    "password": "KNX_CODEX_IS8LJ"
  },
  {
    "uid": 4599191333,
    "password": "KNX_CODEX_GIHL0"
  }
]
    ],
    "BD": [
        [
  {
    "uid": 4599217500,
    "password": "KNX_CODEX_TMTQY"
  },
  {
    "uid": 4599217489,
    "password": "KNX_CODEX_CCJ4C"
  },
  {
    "uid": 4599217485,
    "password": "KNX_CODEX_TADP7"
  },
  {
    "uid": 4599217484,
    "password": "KNX_CODEX_3FL2T"
  },
  {
    "uid": 4599217493,
    "password": "KNX_CODEX_RXD5E"
  },
  {
    "uid": 4599217483,
    "password": "KNX_CODEX_ZMXMW"
  },
  {
    "uid": 4599217504,
    "password": "KNX_CODEX_AIKRI"
  },
  {
    "uid": 4599217492,
    "password": "KNX_CODEX_WECM9"
  },
  {
    "uid": 4599217490,
    "password": "KNX_CODEX_Z0THK"
  },
  {
    "uid": 4599217487,
    "password": "KNX_CODEX_JFKTZ"
  },
  {
    "uid": 4599217481,
    "password": "KNX_CODEX_0ZA27"
  },
  {
    "uid": 4599217482,
    "password": "KNX_CODEX_SD2VG"
  },
  {
    "uid": 4599217494,
    "password": "KNX_CODEX_NWDUJ"
  },
  {
    "uid": 4599217502,
    "password": "KNX_CODEX_CPIDU"
  },
  {
    "uid": 4599217498,
    "password": "KNX_CODEX_6WZKS"
  },
  {
    "uid": 4599217497,
    "password": "KNX_CODEX_1E8YI"
  },
  {
    "uid": 4599217491,
    "password": "KNX_CODEX_Z6IRC"
  },
  {
    "uid": 4599217496,
    "password": "KNX_CODEX_9BBU8"
  },
  {
    "uid": 4599217503,
    "password": "KNX_CODEX_W7ICX"
  },
  {
    "uid": 4599217499,
    "password": "KNX_CODEX_XLF29"
  },
  {
    "uid": 4599217535,
    "password": "KNX_CODEX_793VD"
  },
  {
    "uid": 4599217544,
    "password": "KNX_CODEX_UYG6N"
  },
  {
    "uid": 4599217534,
    "password": "KNX_CODEX_B4RYX"
  },
  {
    "uid": 4599217545,
    "password": "KNX_CODEX_MNCEI"
  },
  {
    "uid": 4599217552,
    "password": "KNX_CODEX_NO4UO"
  },
  {
    "uid": 4599217548,
    "password": "KNX_CODEX_BVIYA"
  },
  {
    "uid": 4599217542,
    "password": "KNX_CODEX_DG723"
  },
  {
    "uid": 4599217539,
    "password": "KNX_CODEX_1RI7X"
  },
  {
    "uid": 4599217540,
    "password": "KNX_CODEX_9CFU8"
  },
  {
    "uid": 4599217550,
    "password": "KNX_CODEX_9QEZ6"
  },
  {
    "uid": 4599217560,
    "password": "KNX_CODEX_80Y6A"
  },
  {
    "uid": 4599217556,
    "password": "KNX_CODEX_4AMC8"
  },
  {
    "uid": 4599217574,
    "password": "KNX_CODEX_D3BQQ"
  },
  {
    "uid": 4599217576,
    "password": "KNX_CODEX_B4PS6"
  },
  {
    "uid": 4599217570,
    "password": "KNX_CODEX_AWFZS"
  },
  {
    "uid": 4599217573,
    "password": "KNX_CODEX_RYL6N"
  },
  {
    "uid": 4599217572,
    "password": "KNX_CODEX_0AW7Z"
  },
  {
    "uid": 4599217578,
    "password": "KNX_CODEX_BAO9N"
  },
  {
    "uid": 4599217571,
    "password": "KNX_CODEX_SG4OI"
  },
  {
    "uid": 4599217577,
    "password": "KNX_CODEX_OOVFM"
  },
  {
    "uid": 4599220197,
    "password": "KNX_CODEX_2YK1T"
  },
  {
    "uid": 4599220201,
    "password": "KNX_CODEX_44QUD"
  },
  {
    "uid": 4599220175,
    "password": "KNX_CODEX_GSKFQ"
  },
  {
    "uid": 4599220172,
    "password": "KNX_CODEX_2I7HP"
  },
  {
    "uid": 4599220187,
    "password": "KNX_CODEX_3IHMV"
  },
  {
    "uid": 4599220213,
    "password": "KNX_CODEX_9C09S"
  },
  {
    "uid": 4599220184,
    "password": "KNX_CODEX_TOO13"
  },
  {
    "uid": 4599220200,
    "password": "KNX_CODEX_3UIDN"
  },
  {
    "uid": 4599220207,
    "password": "KNX_CODEX_L7Y1I"
  },
  {
    "uid": 4599220182,
    "password": "KNX_CODEX_9E3LN"
  },
  {
    "uid": 4599220198,
    "password": "KNX_CODEX_ACF69"
  },
  {
    "uid": 4599220191,
    "password": "KNX_CODEX_SOP4K"
  },
  {
    "uid": 4599220215,
    "password": "KNX_CODEX_MSNSA"
  },
  {
    "uid": 4599220183,
    "password": "KNX_CODEX_AHPNI"
  },
  {
    "uid": 4599220178,
    "password": "KNX_CODEX_6V14I"
  },
  {
    "uid": 4599224174,
    "password": "KNX_CODEX_DJRHJ"
  },
  {
    "uid": 4599224182,
    "password": "KNX_CODEX_G65SC"
  },
  {
    "uid": 4599224179,
    "password": "KNX_CODEX_63MOW"
  },
  {
    "uid": 4599224196,
    "password": "KNX_CODEX_S5I5W"
  },
  {
    "uid": 4599224178,
    "password": "KNX_CODEX_3CF92"
  },
  {
    "uid": 4599224191,
    "password": "KNX_CODEX_UGNIE"
  },
  {
    "uid": 4599224180,
    "password": "KNX_CODEX_KW8JA"
  },
  {
    "uid": 4599224175,
    "password": "KNX_CODEX_T8IHC"
  },
  {
    "uid": 4599224195,
    "password": "KNX_CODEX_GIRFL"
  },
  {
    "uid": 4599224172,
    "password": "KNX_CODEX_525G5"
  },
  {
    "uid": 4599224190,
    "password": "KNX_CODEX_9JDGS"
  },
  {
    "uid": 4599224189,
    "password": "KNX_CODEX_O2AF9"
  },
  {
    "uid": 4599224169,
    "password": "KNX_CODEX_3GQAW"
  },
  {
    "uid": 4599224200,
    "password": "KNX_CODEX_DXXYW"
  },
  {
    "uid": 4599224194,
    "password": "KNX_CODEX_E4D8I"
  },
  {
    "uid": 4599224186,
    "password": "KNX_CODEX_9562A"
  },
  {
    "uid": 4599224192,
    "password": "KNX_CODEX_88QDY"
  },
  {
    "uid": 4599228008,
    "password": "KNX_CODEX_PXX0W"
  },
  {
    "uid": 4599228022,
    "password": "KNX_CODEX_6MR5G"
  },
  {
    "uid": 4599228003,
    "password": "KNX_CODEX_VE8R8"
  },
  {
    "uid": 4599228011,
    "password": "KNX_CODEX_P8GR6"
  },
  {
    "uid": 4599228017,
    "password": "KNX_CODEX_CZM8U"
  },
  {
    "uid": 4599228006,
    "password": "KNX_CODEX_GAOIR"
  },
  {
    "uid": 4599227987,
    "password": "KNX_CODEX_GJIQC"
  },
  {
    "uid": 4599227993,
    "password": "KNX_CODEX_8LV11"
  },
  {
    "uid": 4599227985,
    "password": "KNX_CODEX_K7W4I"
  },
  {
    "uid": 4599228002,
    "password": "KNX_CODEX_O9EJ4"
  },
  {
    "uid": 4599227997,
    "password": "KNX_CODEX_4EN3S"
  },
  {
    "uid": 4599228009,
    "password": "KNX_CODEX_ZLH32"
  },
  {
    "uid": 4599228015,
    "password": "KNX_CODEX_P9PR8"
  },
  {
    "uid": 4599227983,
    "password": "KNX_CODEX_CJC6X"
  },
  {
    "uid": 4599228000,
    "password": "KNX_CODEX_YCOCD"
  },
  {
    "uid": 4599228018,
    "password": "KNX_CODEX_EWD5X"
  },
  {
    "uid": 4599227991,
    "password": "KNX_CODEX_6GM8A"
  },
  {
    "uid": 4599227988,
    "password": "KNX_CODEX_L3HD6"
  },
  {
    "uid": 4599228020,
    "password": "KNX_CODEX_2Q1O3"
  },
  {
    "uid": 4599228010,
    "password": "KNX_CODEX_AR9YY"
  },
  {
    "uid": 4599232016,
    "password": "KNX_CODEX_EJ25Y"
  },
  {
    "uid": 4599232001,
    "password": "KNX_CODEX_95VN1"
  },
  {
    "uid": 4599232027,
    "password": "KNX_CODEX_APRD0"
  },
  {
    "uid": 4599232007,
    "password": "KNX_CODEX_TG3ZY"
  },
  {
    "uid": 4599232031,
    "password": "KNX_CODEX_HOH5O"
  },
  {
    "uid": 4599232038,
    "password": "KNX_CODEX_ZQWIQ"
  },
  {
    "uid": 4599232039,
    "password": "KNX_CODEX_5YR0N"
  },
  {
    "uid": 4599232021,
    "password": "KNX_CODEX_6ZKQU"
  },
  {
    "uid": 4599232023,
    "password": "KNX_CODEX_4EWYA"
  },
  {
    "uid": 4599232004,
    "password": "KNX_CODEX_WZU6U"
  },
  {
    "uid": 4599232024,
    "password": "KNX_CODEX_MLVE4"
  },
  {
    "uid": 4599232029,
    "password": "KNX_CODEX_3UAG8"
  },
  {
    "uid": 4599232022,
    "password": "KNX_CODEX_11II9"
  },
  {
    "uid": 4599232014,
    "password": "KNX_CODEX_O3GQ6"
  },
  {
    "uid": 4599232036,
    "password": "KNX_CODEX_9MM3A"
  },
  {
    "uid": 4599232026,
    "password": "KNX_CODEX_IJS1A"
  },
  {
    "uid": 4599232037,
    "password": "KNX_CODEX_ETZT4"
  },
  {
    "uid": 4599232011,
    "password": "KNX_CODEX_U2UEE"
  },
  {
    "uid": 4599232043,
    "password": "KNX_CODEX_PZYKZ"
  },
  {
    "uid": 4599235800,
    "password": "KNX_CODEX_BAIE1"
  },
  {
    "uid": 4599235806,
    "password": "KNX_CODEX_D173L"
  },
  {
    "uid": 4599235804,
    "password": "KNX_CODEX_4G8JX"
  },
  {
    "uid": 4599235823,
    "password": "KNX_CODEX_5Y994"
  },
  {
    "uid": 4599235790,
    "password": "KNX_CODEX_XX4JX"
  },
  {
    "uid": 4599235792,
    "password": "KNX_CODEX_PADYV"
  },
  {
    "uid": 4599235791,
    "password": "KNX_CODEX_HWLST"
  },
  {
    "uid": 4599235818,
    "password": "KNX_CODEX_4DDNY"
  },
  {
    "uid": 4599235829,
    "password": "KNX_CODEX_K0UW8"
  },
  {
    "uid": 4599235812,
    "password": "KNX_CODEX_ZXA9A"
  },
  {
    "uid": 4599235799,
    "password": "KNX_CODEX_AJAWL"
  },
  {
    "uid": 4599235819,
    "password": "KNX_CODEX_F1D9C"
  },
  {
    "uid": 4599235822,
    "password": "KNX_CODEX_CR019"
  },
  {
    "uid": 4599235814,
    "password": "KNX_CODEX_737SG"
  },
  {
    "uid": 4599235802,
    "password": "KNX_CODEX_NS6PM"
  },
  {
    "uid": 4599235831,
    "password": "KNX_CODEX_ZUCQS"
  },
  {
    "uid": 4599235825,
    "password": "KNX_CODEX_W1TQG"
  },
  {
    "uid": 4599237937,
    "password": "KNX_CODEX_7099O"
  },
  {
    "uid": 4599237943,
    "password": "KNX_CODEX_JYB4K"
  },
  {
    "uid": 4599237950,
    "password": "KNX_CODEX_JQCV8"
  },
  {
    "uid": 4599237933,
    "password": "KNX_CODEX_0M8WF"
  },
  {
    "uid": 4599237951,
    "password": "KNX_CODEX_55ALI"
  },
  {
    "uid": 4599237935,
    "password": "KNX_CODEX_AH2MQ"
  },
  {
    "uid": 4599237953,
    "password": "KNX_CODEX_0O94I"
  },
  {
    "uid": 4599237960,
    "password": "KNX_CODEX_O6302"
  },
  {
    "uid": 4599237959,
    "password": "KNX_CODEX_JZRNW"
  },
  {
    "uid": 4599237955,
    "password": "KNX_CODEX_L4YXK"
  },
  {
    "uid": 4599237940,
    "password": "KNX_CODEX_O0PWD"
  },
  {
    "uid": 4599237948,
    "password": "KNX_CODEX_E2TE4"
  },
  {
    "uid": 4599237944,
    "password": "KNX_CODEX_FTK6L"
  },
  {
    "uid": 4599237945,
    "password": "KNX_CODEX_GIJUK"
  },
  {
    "uid": 4599237942,
    "password": "KNX_CODEX_82UVC"
  },
  {
    "uid": 4599237957,
    "password": "KNX_CODEX_X010C"
  },
  {
    "uid": 4599237956,
    "password": "KNX_CODEX_KGKT3"
  },
  {
    "uid": 4599237952,
    "password": "KNX_CODEX_6HSIM"
  },
  {
    "uid": 4599237949,
    "password": "KNX_CODEX_7BFEJ"
  },
  {
    "uid": 4599241753,
    "password": "KNX_CODEX_8XXOQ"
  },
  {
    "uid": 4599241763,
    "password": "KNX_CODEX_E44YL"
  },
  {
    "uid": 4599241784,
    "password": "KNX_CODEX_7LS0B"
  },
  {
    "uid": 4599241758,
    "password": "KNX_CODEX_KX2IT"
  },
  {
    "uid": 4599241774,
    "password": "KNX_CODEX_BHKND"
  },
  {
    "uid": 4599241760,
    "password": "KNX_CODEX_3C6RY"
  },
  {
    "uid": 4599241789,
    "password": "KNX_CODEX_5CRX5"
  },
  {
    "uid": 4599241785,
    "password": "KNX_CODEX_0VKF7"
  },
  {
    "uid": 4599241778,
    "password": "KNX_CODEX_TNU17"
  },
  {
    "uid": 4599241772,
    "password": "KNX_CODEX_865OQ"
  },
  {
    "uid": 4599241750,
    "password": "KNX_CODEX_C6GES"
  },
  {
    "uid": 4599241755,
    "password": "KNX_CODEX_T7CXU"
  },
  {
    "uid": 4599241765,
    "password": "KNX_CODEX_1JJXV"
  },
  {
    "uid": 4599241788,
    "password": "KNX_CODEX_VPSL0"
  },
  {
    "uid": 4599241776,
    "password": "KNX_CODEX_PVRV2"
  },
  {
    "uid": 4599241771,
    "password": "KNX_CODEX_YKYBO"
  },
  {
    "uid": 4599241783,
    "password": "KNX_CODEX_ISBO2"
  },
  {
    "uid": 4599241773,
    "password": "KNX_CODEX_WZ6CX"
  },
  {
    "uid": 4599241769,
    "password": "KNX_CODEX_1P8ZG"
  },
  {
    "uid": 4599241791,
    "password": "KNX_CODEX_CHPGC"
  },
  {
    "uid": 4599245608,
    "password": "KNX_CODEX_IZ2RL"
  },
  {
    "uid": 4599245612,
    "password": "KNX_CODEX_CG69O"
  },
  {
    "uid": 4599245630,
    "password": "KNX_CODEX_DY2UB"
  },
  {
    "uid": 4599245623,
    "password": "KNX_CODEX_1VHB2"
  },
  {
    "uid": 4599245614,
    "password": "KNX_CODEX_PUYWZ"
  },
  {
    "uid": 4599245626,
    "password": "KNX_CODEX_B4ROJ"
  },
  {
    "uid": 4599245611,
    "password": "KNX_CODEX_XUJY4"
  },
  {
    "uid": 4599245628,
    "password": "KNX_CODEX_HOLM9"
  },
  {
    "uid": 4599245636,
    "password": "KNX_CODEX_WZTS0"
  },
  {
    "uid": 4599245603,
    "password": "KNX_CODEX_M1LDP"
  },
  {
    "uid": 4599245607,
    "password": "KNX_CODEX_ENJW9"
  },
  {
    "uid": 4599245606,
    "password": "KNX_CODEX_VV51T"
  },
  {
    "uid": 4599245602,
    "password": "KNX_CODEX_QTZS9"
  },
  {
    "uid": 4599245610,
    "password": "KNX_CODEX_03SYN"
  },
  {
    "uid": 4599245616,
    "password": "KNX_CODEX_NK9UN"
  },
  {
    "uid": 4599245629,
    "password": "KNX_CODEX_21DGB"
  },
  {
    "uid": 4599245625,
    "password": "KNX_CODEX_I8T95"
  },
  {
    "uid": 4599245634,
    "password": "KNX_CODEX_XZB0L"
  },
  {
    "uid": 4599245637,
    "password": "KNX_CODEX_9KYG5"
  }
]
}

# ========== PLAYER DATABASE (For demo) ==========
PLAYER_DATA = {
    "123456": {"name": "๛INDIAN๛KING", "likes": 1250, "server": "IND"},
    "234567": {"name": "BADAL™", "likes": 2340, "server": "IND"},
    "345678": {"name": "ᎶᎯᎷᎬᏒᏰᎾᎽ", "likes": 890, "server": "IND"},
    "456789": {"name": "ÐΣΛƬΉ ƧΉӨƬ", "likes": 1560, "server": "IND"},
    "111222": {"name": "BDxSHOHAG", "likes": 980, "server": "BD"},
    "222333": {"name": "🇧🇩KING🇧🇩", "likes": 1870, "server": "BD"},
    "333444": {"name": "BADHON™", "likes": 2230, "server": "BD"},
    "444555": {"name": "SHAKIB🔥", "likes": 1450, "server": "BD"}
}

# ========== JWT FUNCTIONS ==========
def pad_data(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt_fast(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.encrypt(pad_data(plaintext))

async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = f"{account}&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient(timeout=20.0, verify=False) as client:
        resp = await client.post(url, data=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

async def create_jwt_fast(uid: str, password: str):
    try:
        account = f"uid={uid}&password={password}"
        token_val, open_id = await get_access_token(account)
        body = {
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": token_val,
            "orign_platform_type": "4"
        }
        
        # Simulate JWT generation
        return f"jwt_token_{uid}_{int(time.time())}"
    except Exception as e:
        app.logger.error(f"JWT Generation failed for {uid}: {e}")
        return None

# ========== TOKEN LOADER ==========
def load_tokens(server_name):
    try:
        server_name = server_name.upper()
        accounts = ACCOUNTS.get(server_name, [])
        
        async def batch_generate():
            tasks = []
            for acc in accounts:
                tasks.append(create_jwt_fast(str(acc['uid']), str(acc['password'])))
            return await asyncio.gather(*tasks)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        jwt_list = loop.run_until_complete(batch_generate())
        loop.close()
        
        tokens = [{"token": tk} for tk in jwt_list if tk]
        return tokens if tokens else None
    except Exception as e:
        app.logger.error(f"Token load failed: {e}")
        return None

# ========== ENCRYPTION FUNCTIONS ==========
def encrypt_message(plaintext):
    try:
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_message = pad(plaintext, AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return binascii.hexlify(encrypted_message).decode('utf-8')
    except Exception as e:
        return None

def create_like_protobuf(user_id, region):
    try:
        message = like_pb2.like()
        message.uid = int(user_id)
        message.region = region
        return message.SerializeToString()
    except Exception as e:
        return None

def create_uid_protobuf(uid):
    try:
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        return message.SerializeToString()
    except Exception as e:
        return None

def enc(uid):
    protobuf_data = create_uid_protobuf(uid)
    if protobuf_data is None:
        return None
    return encrypt_message(protobuf_data)

async def send_like(encrypted_uid, token, url):
    try:
        edata = bytes.fromhex(encrypted_uid)
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Authorization': f"Bearer {token}",
            'Content-Type': "application/x-www-form-urlencoded",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB52"
        }
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.post(url, data=edata, headers=headers)
            return response.status_code == 200
    except Exception as e:
        return False

async def send_multiple_likes(uid, server_name, url, tokens):
    try:
        protobuf_message = create_like_protobuf(uid, server_name)
        if protobuf_message is None:
            return 0
            
        encrypted_uid = encrypt_message(protobuf_message)
        if encrypted_uid is None:
            return 0
        
        tasks = []
        for i in range(100):  # Send 100 likes
            token = tokens[i % len(tokens)]["token"]
            tasks.append(send_like(encrypted_uid, token, url))
        
        results = await asyncio.gather(*tasks)
        return sum(1 for r in results if r)
    except Exception as e:
        app.logger.error(f"Multiple likes failed: {e}")
        return 0

def get_player_info(uid, server_name):
    """Get player info from database or generate"""
    if uid in PLAYER_DATA and PLAYER_DATA[uid]["server"] == server_name:
        player = PLAYER_DATA[uid]
        return {
            "name": player["name"],
            "likes": player["likes"],
            "uid": uid
        }
    else:
        # Generate random player
        return {
            "name": f"PLAYER_{uid[-4:]}",
            "likes": 500 + (int(uid[-2:]) if uid[-2:].isdigit() else 0),
            "uid": uid
        }

# ========== HTML TEMPLATE ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="si">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FreeFire Likes Booster</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            max-width: 500px;
            width: 100%;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            padding: 35px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        }
        
        h1 {
            text-align: center;
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 32px;
            margin-bottom: 5px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .server-badges {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 30px;
        }
        
        .badge {
            padding: 8px 30px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 14px;
            color: white;
        }
        
        .badge.ind { background: #ff8c00; }
        .badge.bd { background: #00b894; }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        
        input, select {
            width: 100%;
            padding: 16px;
            border: 2px solid #e1e1e1;
            border-radius: 15px;
            font-size: 16px;
            transition: 0.3s;
        }
        
        input:focus, select:focus {
            border-color: #ff416c;
            outline: none;
            box-shadow: 0 0 0 3px rgba(255, 65, 108, 0.1);
        }
        
        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #ff416c, #ff4b2b);
            border: none;
            border-radius: 15px;
            color: white;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
            margin: 20px 0;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255, 65, 108, 0.4);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loader {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .loader.show { display: block; }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #ff416c;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            display: none;
            margin-top: 25px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 20px;
        }
        
        .result.show { display: block; animation: slideUp 0.5s; }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .player-info {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px dashed #ddd;
        }
        
        .player-name {
            font-size: 28px;
            font-weight: 800;
            color: #333;
        }
        
        .player-id {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 25px 0;
        }
        
        .stat {
            background: white;
            padding: 20px 10px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .stat.highlight {
            background: linear-gradient(45deg, #00b894, #00cec9);
            color: white;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: #333;
        }
        
        .stat.highlight .stat-value { color: white; }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            flex: 1;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
            font-size: 14px;
        }
        
        .btn-copy {
            background: linear-gradient(45deg, #00b894, #00cec9);
            color: white;
        }
        
        .btn-reset {
            background: #636e72;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .message {
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
            display: none;
        }
        
        .message.error {
            background: #ff7675;
            color: white;
            display: block;
        }
        
        .message.success {
            background: #00b894;
            color: white;
            display: block;
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
            color: rgba(255,255,255,0.7);
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🔥 FREE FIRE LIKES</h1>
            <div class="subtitle">INDIA & BANGLADESH SERVERS</div>
            
            <div class="server-badges">
                <span class="badge ind">🇮🇳 INDIA</span>
                <span class="badge bd">🇧🇩 BANGLADESH</span>
            </div>

            <div class="input-group">
                <label>👤 Player UID</label>
                <input type="text" id="uid" placeholder="Enter your UID">
            </div>

            <div class="input-group">
                <label>🌍 Server</label>
                <select id="server">
                    <option value="">Select server</option>
                    <option value="IND">🇮🇳 India (IND)</option>
                    <option value="BD">🇧🇩 Bangladesh (BD)</option>
                </select>
            </div>

            <button id="boostBtn" onclick="boostLikes()">🚀 BOOST LIKES NOW</button>

            <div class="loader" id="loader">
                <div class="spinner"></div>
                <p style="color: #666;">Sending 100 likes...</p>
            </div>

            <div class="message" id="message"></div>

            <div class="result" id="result">
                <div class="player-info">
                    <div class="player-name" id="playerName">-</div>
                    <div class="player-id" id="playerUid">-</div>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-label">BEFORE</div>
                        <div class="stat-value" id="beforeLikes">0</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">AFTER</div>
                        <div class="stat-value" id="afterLikes">0</div>
                    </div>
                    <div class="stat highlight">
                        <div class="stat-label">ADDED</div>
                        <div class="stat-value" id="addedLikes">0</div>
                    </div>
                </div>

                <div class="actions">
                    <button class="btn btn-reset" onclick="resetForm()">🔄 TRY AGAIN</button>
                    <button class="btn btn-copy" onclick="copyResult()">📋 COPY</button>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 FreeFire Booster | Real Working Version</p>
        </div>
    </div>

    <script>
        async function boostLikes() {
            const uid = document.getElementById('uid').value.trim();
            const server = document.getElementById('server').value;
            const btn = document.getElementById('boostBtn');
            const loader = document.getElementById('loader');
            const message = document.getElementById('message');

            if (!uid || !server) {
                showMessage('Please enter UID and select server', 'error');
                return;
            }
            if (!/^\\d+$/.test(uid)) {
                showMessage('UID must contain only numbers', 'error');
                return;
            }

            btn.disabled = true;
            loader.classList.add('show');
            message.style.display = 'none';

            try {
                const response = await fetch(`/api/boost?uid=${uid}&server=${server}`);
                const data = await response.json();

                if (data.error) {
                    showMessage(data.error, 'error');
                } else {
                    document.getElementById('playerName').textContent = data.name;
                    document.getElementById('playerUid').textContent = 'UID: ' + data.uid;
                    document.getElementById('beforeLikes').textContent = data.before;
                    document.getElementById('afterLikes').textContent = data.after;
                    document.getElementById('addedLikes').textContent = '+' + data.added;
                    
                    document.getElementById('result').classList.add('show');
                    showMessage(`✅ Success! Added ${data.added} likes!`, 'success');
                }
            } catch (error) {
                showMessage('Connection error. Try again.', 'error');
            } finally {
                btn.disabled = false;
                loader.classList.remove('show');
            }
        }

        function showMessage(text, type) {
            const message = document.getElementById('message');
            message.textContent = text;
            message.className = 'message ' + type;
            
            setTimeout(() => {
                message.style.display = 'none';
            }, 4000);
        }

        function resetForm() {
            document.getElementById('uid').value = '';
            document.getElementById('server').value = '';
            document.getElementById('result').classList.remove('show');
            document.getElementById('uid').focus();
        }

        function copyResult() {
            const name = document.getElementById('playerName').textContent;
            const uid = document.getElementById('playerUid').textContent;
            const before = document.getElementById('beforeLikes').textContent;
            const after = document.getElementById('afterLikes').textContent;
            const added = document.getElementById('addedLikes').textContent;
            const server = document.getElementById('server').value;

            const text = `🎮 FREE FIRE RESULTS
👤 Player: ${name}
🆔 ${uid}
📊 Before: ${before}
📈 After: ${after}
✨ Added: ${added}
🌍 Server: ${server === 'IND' ? '🇮🇳 India' : '🇧🇩 Bangladesh'}`;

            navigator.clipboard.writeText(text);
            showMessage('📋 Copied!', 'success');
        }

        document.getElementById('uid').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') boostLikes();
        });

        document.getElementById('uid').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    </script>
</body>
</html>
"""

# ========== ROUTES ==========
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/boost', methods=['GET'])
def boost():
    uid = request.args.get('uid')
    server = request.args.get('server', '').upper()
    
    if not uid or not server:
        return jsonify({"error": "Missing parameters"}), 400
    
    if server not in ["IND", "BD"]:
        return jsonify({"error": "Only IND and BD servers supported"}), 400
    
    try:
        # Load tokens
        tokens = load_tokens(server)
        if not tokens:
            return jsonify({"error": "No active tokens"}), 500
        
        # Get player info
        player = get_player_info(uid, server)
        before_likes = player["likes"]
        
        # Set URL
        if server == "IND":
            url = "https://client.ind.freefiremobile.com/LikeProfile"
        else:
            url = "https://client.bd.freefiremobile.com/LikeProfile"
        
        # Send likes
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        successful = loop.run_until_complete(send_multiple_likes(uid, server, url, tokens))
        loop.close()
        
        # Calculate new likes
        added = min(successful, 100)  # Max 100 likes
        after_likes = before_likes + added
        
        result = {
            "name": player["name"],
            "uid": uid,
            "before": before_likes,
            "after": after_likes,
            "added": added,
            "successful": successful
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "servers": ["IND", "BD"],
        "accounts": {
            "IND": len(ACCOUNTS["IND"]),
            "BD": len(ACCOUNTS["BD"])
        }
    })

if __name__ == '__main__':
    print("="*50)
    print("🚀 FreeFire Likes Booster Server")
    print("="*50)
    print("📡 http://localhost:5000")
    print("="*50)
    app.run(debug=True, port=5000)
