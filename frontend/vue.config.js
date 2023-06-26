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
    // proxy: 'http://127.0.0.1:3333',
    proxy: 'http://127.0.0.1:8383', // TODO: (@besrabasant) - Configure this with .env files
    disableHostCheck: true
  },
  lintOnSave: false,
  outputDir: './dist/',
  assetsDir: 'static',
}
