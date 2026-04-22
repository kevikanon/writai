<template>
  <v-app>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>WritAi</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="!authStore.isAuthenticated" variant="text" to="/login">Login</v-btn>
      <v-btn v-if="!authStore.isAuthenticated" variant="outlined" to="/register">Register</v-btn>
      <v-btn v-if="authStore.isAuthenticated" variant="text" to="/articles">Articles</v-btn>
      <v-btn v-if="authStore.isAuthenticated" variant="text" to="/settings">Settings</v-btn>
      <v-btn v-if="authStore.isAuthenticated" variant="text" @click="handleLogout">Logout</v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>