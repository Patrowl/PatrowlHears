<template>
  <v-snackbar v-model="_snack.model" :timeout="_snack.timeout" :color="_snack.color">
    {{ _snack.text }}
    <v-btn text @click="_snack.model = false">Close</v-btn>
  </v-snackbar>
</template>

<script>

export default {
  name: "PSnackBar",
  props: [
    'snack'
  ],
  data: () => ({
    // snack: { model: false, color: '', text: '', timeout: 3000 }
  }),
  mounted() {
  },
  computed: {
    _snack: {
      get () {
        return this.snack
      },
      set (value) {
        if (!value) {
          this.$emit('close')
        }
      }
    }
  },
  watch: {
    snack: function(){
      this._snack = this.snack
    }
  },
  methods: {
  }
};
</script>

<style>
</style>
