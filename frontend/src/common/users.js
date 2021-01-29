export default {
  methods: {
    isAdmin() {
      return localStorage.getItem('is_admin');
    },
    isOrgAdmin() {
      return localStorage.getItem('is_org_admin');
    },
    getUserProfile() {
      return localStorage.getItem('profile');
    },
    
  },
  mounted() {

  },
  destroyed() {

  }
};
