<template>
    <div>
        Homepage
    </div>
</template>

<script>
import router from "../../router";
export default {
  name: "Home",
  mounted() {
    // this.checkLoggedIn();
  },
  methods: {
    // checkLoggedIn() {
    //   this.$session.start();
    //   if (!this.$session.has("token")) {
    //     router.push("/auth");
    //   }
    // }
  }
};
</script>
