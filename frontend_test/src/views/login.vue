<template>
    <div class="position-static">
    <!-- <div class="position-absolute top-50 start-100"> -->
  <div class="login">
      <div class="card align-middle">
        <h3>login page</h3>
    <form @submit.prevent="loginUser">
      <div>
        <label>Email:</label>
        <input type="email" v-model="email" required />
      </div><br>
      <div>
        <label>Password:</label>
        <input type="password" v-model="password" required />
      </div><br>
      <button type="submit">Login</button>
    </form>
    <p v-if="message">{{ message }}</p>
  </div>
</div>
</div>
</template>
<script>
    import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/apis';


export default {
  data() {
    return {
      email: '',
      password: '',
      message: ''
    };
  },
  methods: {
    // ...mapMutations(['setUserData']), // Map the setUserRole mutation
    loginUser() {
        // axios.post('http://localhost:5000/api/login'  axios.post().then().catch()
      axios.post(`${API_BASE_URL}/login`, {
        email: this.email,
        password: this.password,
      })
        .then(response => {
          this.message = response.data.message;
          // Clear the form fields after successful login
          this.email = '';
          this.password = '';
          // Perform any other actions after successful login
          localStorage.setItem('userRole', response.data.roles[0]);
          localStorage.setItem('authToken', response.data.auth_token);
          localStorage.setItem('userId', response.data.id);
          // this.setUserData(response.data.roles.includes('admin') ? 'admin' : 'user'); // Set the user role
          // this.setAuthTokenInCookie(response.data.auth_token); // Set the auth token in cookie
          this.$router.push(response.data.roles.includes('admin') ? '/dashboard' : '/home'); // Redirect to '/dashboard'
        })
        .catch(error => {
          if (error.response && error.response.data.message) {
            this.message = error.response.data.message;
          } else {
            this.message = error.message;
          }
        });
    },
  },
};
</script>
