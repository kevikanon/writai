<template>
  <v-container fluid class="login-page">
    <v-row no-gutters class="fill-height">
      <v-col cols="12" class="d-flex align-center justify-center">
        <v-card class="pa-8" elevation="4" width="100%" max-width="450">
          <v-card-title class="text-h4 text-center mb-4">Reset Password</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleReset">
              <v-text-field
                v-model="password"
                label="New Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                density="comfortable"
                required
                class="mb-2"
              />
              <v-text-field
                v-model="confirmPassword"
                label="Confirm Password"
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
                Reset Password
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { success: showSuccess, error: showError } = useToast()

const password = ref('')
const confirmPassword = ref('')

const handleReset = async () => {
  if (password.value !== confirmPassword.value) {
    showError('Passwords do not match')
    return
  }
  const result = await authStore.resetPassword(route.params.token, password.value)
  if (result.success) {
    showSuccess('Password reset successfully')
    setTimeout(() => router.push('/login'), 2000)
  } else {
    showError(result.error)
  }
}
</script>

<style scoped>
.login-page {
  height: calc(100vh - 48px);
  overflow: hidden;
}
</style>