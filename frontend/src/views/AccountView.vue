<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { signIn } from '../auth/session'

const props = defineProps({ register: Boolean })
const route = useRoute()
const router = useRouter()

const notice = ref(false)
const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

// Only allow redirects to paths inside this app (no "//evil.example").
function redirectTarget() {
  const target = route.query.redirect
  return typeof target === 'string' && target.startsWith('/') && !target.startsWith('//')
    ? target
    : '/app'
}

async function submit() {
  if (props.register) {
    // Registration is handled in BIZ-24 / BIZ-12; still a preview here.
    notice.value = true
    return
  }

  error.value = ''
  submitting.value = true
  try {
    await signIn(email.value, password.value)
    await router.replace(redirectTarget())
  } catch (err) {
    error.value = err.message
    password.value = ''
  } finally {
    submitting.value = false
  }
}

function clearMessages() {
  notice.value = false
  error.value = ''
}
</script>

<template>
  <main class="account">
    <section aria-labelledby="account-title">
      <RouterLink to="/">← Back to home</RouterLink>
      <h1 id="account-title">{{ register ? 'Create an account' : 'Log in' }}</h1>
      <p v-if="register">Verify your email before setting a password.</p>
      <form @submit.prevent="submit" @input="clearMessages">
        <div v-if="register" class="names">
          <label>First name <input name="firstName" autocomplete="given-name" required /></label>
          <label>Last name <input name="lastName" autocomplete="family-name" required /></label>
        </div>
        <label>Work email <input v-model="email" name="email" type="email" :autocomplete="register ? 'email' : 'username'" required /></label>
        <label v-if="register">Organization number <input name="organizationNumber" required /></label>
        <label v-else>Password <input v-model="password" name="password" type="password" autocomplete="current-password" required /></label>
        <button class="button" type="submit" :disabled="submitting">
          {{ register ? 'Continue' : submitting ? 'Logging in…' : 'Log in' }}
        </button>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <p v-if="notice" class="notice" role="status">This form is a preview. Account services are pending.</p>
      </form>
      <p class="switch">
        {{ register ? 'Already have an account?' : 'New to BizPartnerCheck?' }}
        <RouterLink :to="register ? '/login' : '/register'">
          {{ register ? 'Log in' : 'Create an account' }}
        </RouterLink>
      </p>
    </section>
  </main>
</template>

<style scoped>
.account { min-height: calc(100svh - 76px); padding: 44px 16px; display: grid; place-items: start center; background: linear-gradient(#b1d3f44a 1px, transparent 1px), linear-gradient(90deg, #b1d3f44a 1px, transparent 1px), #eaf4fd; background-size: 24px 24px; }
section { width: min(100%, 500px); border: 1px solid #c6d9ee; border-radius: 16px; padding: clamp(22px, 5vw, 40px); background: white; box-shadow: 0 18px 52px #17498214; }
h1 { margin-top: 20px !important; font-size: clamp(2rem, 5vw, 2.75rem); }
form, label { display: grid; gap: 8px; }
form { gap: 16px; }
label { min-width: 0; font-weight: 600; }
input { width: 100%; min-width: 0; border: 1px solid #93abc9; border-radius: 7px; background: #f7fbff; padding: 11px 12px; font: inherit; color: inherit; }
.names { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.switch { margin: 20px 0 0; }
.notice { margin: 0; background: #eaf4fd; padding: 12px; border-radius: 7px; }
.error { margin: 0; background: #fdecec; border: 1px solid #e3a5a5; color: #8a1c1c; padding: 12px; border-radius: 7px; }
button:disabled { opacity: .7; cursor: wait; }
@media (max-width: 390px) { .names { grid-template-columns: 1fr; } }
</style>
