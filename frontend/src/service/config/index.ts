
let BASE_URL = ''
if (import.meta.env.PROD) {
    BASE_URL = 'http://127.0.0.1:8000/'
} else {
    BASE_URL = 'http://127.0.0.1:8000/'
}

export const TIME_OUT = 10000
export { BASE_URL }