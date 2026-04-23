import { ref, reactive } from 'vue'

const toastState = reactive({
  show: false,
  text: '',
  color: 'error',
  timeout: 4000,
})

export function useToast() {
  const show = (text, color = 'error', timeout = 4000) => {
    toastState.text = text
    toastState.color = color
    toastState.timeout = timeout
    toastState.show = true
  }

  const success = (text) => show(text, 'success', 3000)
  const error = (text) => show(text, 'error')
  const info = (text) => show(text, 'info')
  const warning = (text) => show(text, 'warning')

  return { toastState, show, success, error, info, warning }
}