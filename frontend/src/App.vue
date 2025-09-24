<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { tryAutoLogin } from './stores/user.js'
tryAutoLogin()
</script>

<style scoped>
/* No navbar styles here */
</style>
