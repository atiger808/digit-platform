import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from "unplugin-vue-components/resolvers";
const pathResolve = (dir) => {
    return resolve(__dirname, '.', dir);
};
const alias = {
    '@': pathResolve('./src/'),
    '@views': pathResolve('./src/views')
};
// https://vite.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        AutoImport({
            resolvers: [ElementPlusResolver()],
        }),
        Components({
            resolvers: [ElementPlusResolver()],
        }),
    ],
    resolve: { alias },
    server: {
        host: true, // 等同于 '0.0.0.0'
        port: 5174,
        allowedHosts: ['digit.first-iq.com', 'vpn.newdmy.com', 'first-iq.com']
    }
});
