<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { createClient } from '@supabase/supabase-js'

const route = useRoute()
const router = useRouter()
const state = ref('loading')
const email = ref('')
const password = ref('')
const confirmation = ref('')
const message = ref('')
const submitting = ref(false)

let client

onMounted(async () => {
  const params = new URLSearchParams(route.hash.slice(1))

  console.info('Supabase invite', {
    type: params.get('type'),
    errorCode: params.get('error_code'),
    hasAccessToken: params.has('access_token'),
    hasRefreshToken: params.has('refresh_token'),
  })

  const accessToken = params.get('access_token')
  const refreshToken = params.get('refresh_token')
  const isInvite = params.get('type') === 'invite'

  if (route.hash) {
    await router.replace({ path: '/set-password' })
  }

  if (!isInvite || !accessToken || !refreshToken) {
    state.value = 'invalid'
    return
  }

  const url = import.meta.env.VITE_SUPABASE_URL
  const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY

  if (!url || !key) {
    state.value = 'configuration-error'
    return
  }

  client = createClient(url, key, {
    auth: {
      detectSessionInUrl: false,
      persistSession: false,
      autoRefreshToken: false,
    },
  })

  try {
    const { data, error } = await client.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken,
    })

    if (error || !data.user?.email_confirmed_at) {
      state.value = 'invalid'
      return
    }

    email.value = data.user.email
    state.value = 'password'
  } catch {
    state.value = 'invalid'
  }
})

async function savePassword() {
  message.value = ''
  if (password.value !== confirmation.value) {
    message.value = 'The passwords do not match.'
    return
  }

  submitting.value = true
  try {
    const { error } = await client.auth.updateUser({ password: password.value })
    if (error) {
      message.value = 'Could not set your password. Check the password requirements or ask for a new link.'
      return
    }
    password.value = ''
    confirmation.value = ''
    state.value = 'done'
    await client.auth.signOut({ scope: 'local' })
  } catch {
    if (state.value !== 'done') {
      message.value = 'Could not set your password. Please try again.'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="setup">
    <section aria-labelledby="setup-title">
      <h1 id="setup-title">Set your password</h1>
      <p v-if="state === 'loading'" role="status">Opening your invitation…</p>
      <p v-else-if="state === 'invalid'" role="alert">
        Open the invitation link sent to your email address.
      </p>
      <p v-else-if="state === 'configuration-error'" role="alert">
        Email verification is unavailable. Contact the team.
      </p>
      <form v-else-if="state === 'password'" @submit.prevent="savePassword">
        <p role="status">Email verified for {{ email }}.</p>
        <label>
          New password
          <input v-model="password" type="password" autocomplete="new-password" minlength="12" required />
        </label>
        <label>
          Repeat password
          <input v-model="confirmation" type="password" autocomplete="new-password" minlength="12" required />
        </label>
        <button class="button" type="submit" :disabled="submitting">
          {{ submitting ? 'Saving…' : 'Save password' }}
        </button>
      </form>
      <p v-else-if="state === 'done'" role="status">Your password has been saved.</p>
      <p v-if="message" role="alert">{{ message }}</p>
      <RouterLink to="/">Back to home</RouterLink>
    </section>
  </main>
</template>

<style scoped>
.setup { max-width: 520px; margin: 42px auto; padding: 0 16px; }
section { display: grid; gap: 16px; padding: 28px; background: white; border: 1px solid #c6d9ee; border-radius: 16px; }
form, label { display: grid; gap: 8px; }
form { gap: 16px; }
input { padding: 10px 12px; border: 1px solid #93abc9; border-radius: 7px; font: inherit; }
</style>