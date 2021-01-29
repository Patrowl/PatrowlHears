export default {
  methods: {
    forceFileDownload(response, title) {
      const url = window.URL.createObjectURL(new Blob([response.data], {type:'application/*'}));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', title);
      document.body.appendChild(link);
      link.click();
    },
  },
  mounted() {

  },
  destroyed() {

  }
};
