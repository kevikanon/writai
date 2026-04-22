<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6" xl="4">
        <v-card class="pa-8" elevation="4">
          <v-card-title class="text-h4 text-center mb-4">Register</v-card-title>
          <v-card-text>
            <v-alert v-if="authStore.error" type="error" class="mb-4">
              {{ authStore.error }}
            </v-alert>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="name"
                label="Name"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                density="comfortable"
                required
                class="mb-2"
              />
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
                Register
              </v-btn>
            </v-form>
            <div class="text-center mt-6">
              Already have an account? <router-link to="/login">Login</router-link>
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

const router = useRouter()
const authStore = useAuthStore()

const name = ref('')
const email = ref('')
const password = ref('')

const handleRegister = async () => {
  const success = await authStore.register(name.value, email.value, password.value)
  if (success) {
    router.push('/articles')
  }
}
</script>