<template>
  <v-container fluid class="login-page">
    <v-row no-gutters class="fill-height">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="pa-8" elevation="4" width="100%" max-width="450">
          <v-card-title class="text-h4 text-center mb-4">Forgot Password</v-card-title>
          <v-card-text>
            <v-alert v-if="authStore.error" type="error" class="mb-4">
              {{ authStore.error }}
            </v-alert>
            <v-alert v-if="success" type="success" class="mb-4">
              Password reset link sent to your email
            </v-alert>
            <v-form @submit.prevent="handleForgot">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
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
                Send Reset Link
              </v-btn>
            </v-form>
            <div class="text-center mt-6">
              <router-link to="/login">Back to Login</router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const email = ref('')
const success = ref(false)

const handleForgot = async () => {
  success.value = await authStore.forgotPassword(email.value)
}
</script>

<style scoped>
.login-page {
  height: calc(100vh - 48px);
  overflow: hidden;
}
</style>