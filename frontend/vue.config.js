module.exports = {
  "transpileDependencies": [
    "vuetify",
    'vue-clamp',
    'resize-detector'
  ],
  // baseUrl: process.env.NODE_ENV === 'production'
  //   ? '/'
  //   : 'http://localhost:3333',

  devServer: {
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
    proxy: 'http://127.0.0.1:3333'
    // proxy: {
    //   '^/api/': {
    //     target: 'http://127.0.0.1:3333/api/',
    //   }
    // }
  },
  lintOnSave: false,
  outputDir: './dist/',
  assetsDir: 'static',
}
