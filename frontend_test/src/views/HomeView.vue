<template>
  <div class="home">
    <p>this is from homeview.vue that is present inside view dir</p>
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App, updated"/>
    <p>this is the edning homeview.vue that is present inside view dir</p>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'HomeView',
  components: {
    HelloWorld
  }
}
</script>
