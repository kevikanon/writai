<template>
  <v-snackbar
    v-model="toastState.show"
    :color="toastState.color"
    :timeout="toastState.timeout"
    location="top"
  >
    {{ toastState.text }}
    <template v-slot:actions>
      <v-btn variant="text" @click="toastState.show = false">Close</v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toastState } = useToast()
</script>