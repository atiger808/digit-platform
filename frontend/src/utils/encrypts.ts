import CryptoJS from "crypto-js";
import CryptoSM from 'sm-crypto'


const object2string = (data) => {
    if(typeof data === 'object'){
        return JSON.stringify(data)
    }

    let str = JSON.stringify(data)
    if(str.startsWith("'") || str.startsWith('"')) {
        str = str.substring(1)
    }
    if (str.endsWith("'") || str.endsWith('"')) {
        str = str.substring(0, str.length - 1)
    }
    return str
}


/**
 * 字符串转数字
 */
const stringToHex = (str) => {
    let hex = ''
    for(let i = 0; i < str.length; i++){
        hex += str.charCodeAt(i).toString(16).padStart(2, '0')
    }
    return hex
}

/**
 * -------------------- ※ AES 加密、解密 begin ※ --------------------
 *
 * 1. AES 加密算法支持三种密钥长度：128、192、256，这里选择128位密钥。
 * 2. AES 加密算法支持三种填充模式：Pkcs7、Iso10126、ZeroPadding，这里选择Pkcs7。
 * 3. AES 加密算法支持三种工作模式：ECB、CBC、CFB，这里选择ECB。
 * 4. AES 要求秘钥为128bit,转换字节为16个字节，即16个字符。
 * 5. js前端使用 UCS-2 或者 UTF-16编码，字母，数字，特殊符号等 占用1个字节
 * 6. 所以：秘钥Key 组成为：16个字符，即16个字节，即128bit。
 *
 * -------------------- ※ AES 加密、解密 end ※ --------------------
 */
const AES_KEY = '1234567890abcdef'

const AES = {

    encryptData: function (data) {
        // AES 加密 并转为base64
        let utf8Data = CryptoJS.enc.Utf8.parse(object2string(data))
        const key = CryptoJS.enc.Utf8.parse(AES_KEY)
        const encrypted = CryptoJS.AES.encrypt(utf8Data, key, {
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7
        })
        return CryptoJS.enc.Base64.stringify(encrypted.ciphertext)
    },

    decryptData: function (data) {
        // 第一步：base64解码
        let base64Data = CryptoJS.enc.Base64.parse(data)

        // 第二步：AES 解密
        const key = CryptoJS.enc.Utf8.parse(AES_KEY)
        return CryptoJS.AES.decrypt({ciphertext: base64Data}, key, {
            mode: CryptoJS.mode.ECB,
            padding: CryptoJS.pad.Pkcs7
        }).toString(CryptoJS.enc.Utf8)
    },

};


/**
 * -------------------- ※ 国密SM4算法 加密、解密 begin ※ --------------------
 *
 * 1. 国密SM4算法支持三种密钥长度：128、192、256，这里选择128位密钥。
 * 2. 国密SM4算法支持三种填充模式：NoPadding、ZeroPadding，这里选择ZeroPadding。
 * 3. 国密SM4算法支持三种工作模式：ECB、CBC、CFB，这里选择ECB。
 * 4. 国密SM4 算法要求秘钥为128bit,转换字节为16个字节，即16个字符。
 *
 * -------------------- ※ 国密SM4算法 加密、解密 end ※ --------------------
 */

// 国密SM4 算法秘钥组成为: 16个字符，即16个字节，即128bit。
const SM4_KEY = '1234567890abcdef'

const SM4 = {

    encryptData: function (data) {
        // 第一步：国密SM4 加密
        let encryptData = CryptoSM.sm4.encrypt(object2string(data), stringToHex(SM4_KEY))
        // 第二步：base64编码
        return CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(encryptData))

    },

    decryptData: function (data) {
        // 第一步：Base64 解码
        let base64Data = CryptoJS.enc.Base64.parse(data)
        let decode64Str = CryptoJS.enc.Utf8.stringify(base64Data)

        // 第二步：国密SM4 解密
        return CryptoSM.sm4.decrypt(decode64Str, stringToHex(SM4_KEY))
    },
};

// -----------------------  对外暴露： 加密、解密 -----------------------

// 默认使用SM4算法
// const EncyptObject = SM4

// 默认使用AES算法
const EncyptObject = AES

/**
 * 加密
 */

export const encryptData = (data) => {
    return !data ? null : EncyptObject.encryptData(data)
}

/**
 * 解密
 */

export const decryptData = (data) => {
    return !data ? null : EncyptObject.decryptData(data)
}
