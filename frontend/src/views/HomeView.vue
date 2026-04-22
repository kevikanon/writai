<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" md="8" lg="6" class="text-center">
        <h1 class="text-h3 font-weight-bold mb-4">AI Writing & SEO Suite</h1>
        <p class="text-h6 text-grey-darken-1 mb-8">
          Create SEO-optimized content with AI-powered generators
        </p>
        <v-btn
          v-if="!authStore.isAuthenticated"
          color="primary"
          size="large"
          to="/register"
          class="mr-4"
        >
          Get Started
        </v-btn>
        <v-btn
          v-if="!authStore.isAuthenticated"
          variant="outlined"
          size="large"
          to="/login"
        >
          Login
        </v-btn>
        <v-btn
          v-if="authStore.isAuthenticated"
          color="primary"
          size="large"
          to="/articles"
        >
          Go to Articles
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>