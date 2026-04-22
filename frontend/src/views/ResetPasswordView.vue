<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-4">
          <v-card-title class="text-h5 text-center">Reset Password</v-card-title>
          <v-card-text>
            <v-alert v-if="authStore.error" type="error" class="mb-4">
              {{ authStore.error }}
            </v-alert>
            <v-alert v-if="success" type="success" class="mb-4">
              Password reset successfully
            </v-alert>
            <v-form @submit.prevent="handleReset">
              <v-text-field
                v-model="password"
                label="New Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-text-field
                v-model="confirmPassword"
                label="Confirm Password"
                type="password"
                prepend-inner-icon="mdi-lock"
                required
              />
              <v-btn
                type="submit"
                color="primary"
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

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const password = ref('')
const confirmPassword = ref('')
const success = ref(false)

const handleReset = async () => {
  if (password.value !== confirmPassword.value) {
    authStore.error = 'Passwords do not match'
    return
  }
  success.value = await authStore.resetPassword(route.params.token, password.value)
  if (success.value) {
    setTimeout(() => router.push('/login'), 2000)
  }
}
</script>