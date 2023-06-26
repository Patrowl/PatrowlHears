<template>
  <v-app>
    <router-view></router-view>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  data () {
    return {
      section: 'AppLayout'
    }
  },
  created () {
    document.title = "CanPatch";
  },
  methods: {
    logout() {
      this.$store.commit("removeToken");
      this.$router.push('/auth');
    }
  }
}
</script>

<style lang="sass">
  @import '../node_modules/typeface-roboto/index.css'
</style>
