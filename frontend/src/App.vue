<template>
  <v-app>
    <Toast />
    <CommandPalette ref="commandPalette" />
    <v-app-bar color="primary" density="compact">
      <v-app-bar-title>WritAi</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="authStore.isAuthenticated" variant="text" @click="openCommandPalette">
        <v-icon icon="mdi-magnify" class="mr-1" />
        <span class="text-caption">Ctrl+K</span>
      </v-btn>
      <v-btn v-if="!authStore.isAuthenticated" variant="text" to="/login">Login</v-btn>
      <v-btn v-if="!authStore.isAuthenticated" variant="outlined" to="/register">Register</v-btn>
      <v-btn v-if="authStore.isAuthenticated" variant="text" to="/craft">Craft</v-btn>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import Toast from './components/Toast.vue'
import CommandPalette from './components/CommandPalette.vue'

const router = useRouter()
const authStore = useAuthStore()
const commandPalette = ref(null)

const openCommandPalette = () => {
  commandPalette.value?.open()
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>