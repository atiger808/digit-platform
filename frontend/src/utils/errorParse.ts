export const errorParse = (error) => {
    let errorInfo = '';
    if (typeof error === 'object' && error.length > 0) {
        errorInfo = error.join(',');
    } else if (error.hasOwnProperty('response')) {
        if (error.response.data.hasOwnProperty('detail')) {
            errorInfo = typeof error.response.data.detail === 'string' ? error.response.data.detail :  error.response.data.detail[0]
        } else if (error.response.data.hasOwnProperty('error')) {
            errorInfo = typeof error.response.data.error === 'string' ? error.response.data.error :  error.response.data.error[0]
        } else if (error.response.data.hasOwnProperty('msg')) {
            errorInfo = typeof error.response.data.msg === 'string' ? error.response.data.msg :  error.response.data.msg[0]
        } else if (error.response.data.hasOwnProperty('username')) {
            errorInfo = typeof error.response.data.username === 'string' ? error.response.data.username :  error.response.data.username[0]
        } else if (error.response.data.hasOwnProperty('email')) {
            errorInfo = typeof error.response.data.email === 'string' ? error.response.data.email :  error.response.data.email[0]
        } else if (error.response.data.hasOwnProperty('real_name')) {
            errorInfo = typeof error.response.data.real_name === 'string' ? error.response.data.real_name :  error.response.data.real_name[0]
        } else if (error.response.data.hasOwnProperty('password')) {
            errorInfo = typeof error.response.data.password === 'string' ? error.response.data.password :  error.response.data.password[0]
        } else if (error.response.data.hasOwnProperty('mobile')) {
            errorInfo = typeof error.response.data.mobile === 'string' ? error.response.data.mobile :  error.response.data.mobile[0]
        } else if (error.response.data.hasOwnProperty('code')) {
            errorInfo = typeof error.response.data.code === 'string' ? error.response.data.code :  error.response.data.code[0]
        } else if (error.response.data.hasOwnProperty('captcha')) {
            errorInfo = typeof error.response.data.captcha === 'string' ? error.response.data.captcha :  error.response.data.captcha[0]
        } else if (error.response.data.hasOwnProperty('code')) {
            errorInfo = typeof error.response.data.code === 'string' ? error.response.data.code :  error.response.data.code[0]
        } else if (error.response.data.hasOwnProperty('password2')) {
            errorInfo = typeof error.response.data.password2 === 'string' ? error.response.data.password2 :  error.response.data.password2[0]
        } else if (error.response.data.hasOwnProperty('old_password')) {
            errorInfo = typeof error.response.data.old_password === 'string' ? error.response.data.old_password :  error.response.data.old_password[0]
        } else if (error.response.data.hasOwnProperty('vpn_account')) {
            errorInfo = typeof error.response.data.vpn_account === 'string' ? error.response.data.vpn_account :  error.response.data.vpn_account[0]
        } else if (error.response.data.hasOwnProperty('vpn_pwd')) {
            errorInfo = typeof error.response.data.vpn_pwd === 'string' ? error.response.data.vpn_pwd :  error.response.data.vpn_pwd[0]
        } else if (error.hasOwnProperty('message')) {
            errorInfo = error.message
        } else {
            errorInfo = Object.values(error.response.data).map(arr => arr[0]).join(',')
        }
    } else {
        errorInfo = error.message
    }
    return errorInfo
}