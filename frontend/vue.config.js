module.exports = {
  "transpileDependencies": [
    "vuetify",
    'vue-clamp', 'resize-detector'
  ],
  // baseUrl: process.env.NODE_ENV === 'production'
  //   ? '/'
  //   : 'http://localhost:3333',

  devServer: {
    headers: {
      'Access-Control-Allow-Origin': '*',
    }
  },
  lintOnSave: false
}
