export default {
  methods: {
    getCVSSColor(score) {
      if (score >= 9.0 ) return 'red darken-4';
      else if (score >= 7.0) return 'red';
      else if (score >= 4.0) return 'orange';
      else if (score >= 0.1) return 'yellow';
      else return 'grey';
    },
    getTLPColor(tlp_level) {
      if (tlp_level === 'white' ) return '';
      else if (tlp_level === 'green') return 'green';
      else if (tlp_level === 'amber') return 'orange';
      else if (tlp_level === 'red') return 'red';
      else if (tlp_level === 'black') return 'black';
      else return 'grey';
    },
    getRatingColor(rating) {
      if (rating >= 80 ) return 'red';
      else if (rating >= 60) return 'orange';
      else if (rating >= 40) return 'yellow';
      else if (rating >= 0) return 'blue';
      else return 'grey';
    },
    getBoolColor(b) {
      if (b) {
        return 'deep-orange';
      } else {
        return 'grey';
      }
    },
    getNumberColor(number) {
      if ( number > 0 ){
        return "deep-orange";
      } else {
        return "grey"
      }
    }
  },
  mounted() {

  },
  destroyed() {

  }
};
