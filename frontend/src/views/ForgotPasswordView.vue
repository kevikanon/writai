<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="pa-4">
          <v-card-title class="text-h5 text-center">Forgot Password</v-card-title>
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
                required
              />
              <v-btn
                type="submit"
                color="primary"
                block
                :loading="authStore.loading"
              >
                Send Reset Link
              </v-btn>
            </v-form>
            <div class="text-center mt-4">
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