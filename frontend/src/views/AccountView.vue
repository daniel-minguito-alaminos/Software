<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

defineProps({ register: Boolean })
const notice = ref(false)
</script>

<template>
  <main class="account">
    <section aria-labelledby="account-title">
      <RouterLink to="/">← Back to home</RouterLink>
      <h1 id="account-title">{{ register ? 'Create an account' : 'Log in' }}</h1>
      <p v-if="register">Verify your email before setting a password.</p>
      <form @submit.prevent="notice = true" @input="notice = false">
        <div v-if="register" class="names">
          <label>First name <input name="firstName" autocomplete="given-name" required /></label>
          <label>Last name <input name="lastName" autocomplete="family-name" required /></label>
        </div>
        <label>Work email <input name="email" type="email" :autocomplete="register ? 'email' : 'username'" required /></label>
        <label v-if="register">Organization number <input name="organizationNumber" required /></label>
        <label v-else>Password <input name="password" type="password" autocomplete="current-password" required /></label>
        <button class="button" type="submit">{{ register ? 'Continue' : 'Log in' }}</button>
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
@media (max-width: 390px) { .names { grid-template-columns: 1fr; } }
</style>
