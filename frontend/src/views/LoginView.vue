<template>
  <v-container fluid class="login-page">
    <v-row no-gutters class="fill-height">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="pa-8" elevation="4" width="100%" max-width="450">
          <v-card-title class="text-h4 text-center mb-4">Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                density="comfortable"
                required
                class="mb-2"
              />
              <v-text-field
                v-model="password"
                label="Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                density="comfortable"
                required
                class="mb-4"
              />
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="authStore.loading"
              >
                Login
              </v-btn>
            </v-form>
            <div class="text-center mt-6">
              <router-link to="/forgot-password">Forgot Password?</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'

const router = useRouter()
const authStore = useAuthStore()
const { success, error } = useToast()

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  const result = await authStore.login(email.value, password.value)
  if (result.success) {
    success('Login successful!')
    router.push('/articles')
  } else {
    error(result.error)
  }
}
</script>

<style scoped>
.login-page {
  height: calc(100vh - 48px);
  overflow: hidden;
}
</style>