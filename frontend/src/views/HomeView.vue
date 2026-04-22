<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" class="text-center">
        <h1 class="text-h2 font-weight-bold mb-6">AI Writing & SEO Suite</h1>
        <p class="text-h5 text-grey-darken-1 mb-8">
          Create SEO-optimized content with AI-powered generators
        </p>
        <div v-if="!authStore.isAuthenticated">
          <v-btn
            color="primary"
            size="x-large"
            to="/register"
            class="mr-4"
          >
            Get Started
          </v-btn>
          <v-btn
            variant="outlined"
            size="x-large"
            to="/login"
          >
            Login
          </v-btn>
        </div>
        <v-btn
          v-if="authStore.isAuthenticated"
          color="primary"
          size="x-large"
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