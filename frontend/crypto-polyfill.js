// @File   :crypto-polyfill.js
// @Time   :2025/5/9 15:00
// @Author :dayue
// @Email  :ole211@qq.com

const { Crypto } = require('@peculiar/webcrypto');
global.crypto = new Crypto();