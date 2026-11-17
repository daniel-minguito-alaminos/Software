<script setup>
import { ref } from 'vue'

const vatNumber = ref('')
const checking = ref(false)
const message = ref('')

const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

async function checkVat() {
  checking.value = true
  message.value = ''

  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, '')}/checks/vat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vat_number: vatNumber.value.trim() }),
    })

    const result = await response.json()

    if (!response.ok) {
      message.value = typeof result.detail === 'string'
        ? result.detail
        : 'The VAT check could not be completed. Please try again.'
      return
    }

    if (result.valid === true) {
      message.value = 'VAT number is valid in VIES.'
    } else if (result.valid === false) {
      message.value = 'VAT number is not valid in VIES.'
    } else {
      message.value = 'The backend returned an unexpected result.'
    }
  } catch {
    message.value = 'Could not get a response from the backend.'
  } finally {
    checking.value = false
  }
}
</script>

<template>
  <section class="vat-check">
    <h2>Check a VAT / UID number</h2>

    <form @submit.prevent="checkVat">
      <label for="vat-number">VAT / UID number</label>
      <input
        id="vat-number"
        v-model="vatNumber"
        type="text"
        placeholder="ATU37552304"
        required
      />
      <button class="button" type="submit" :disabled="checking">
        {{ checking ? 'Checking…' : 'Check VAT' }}
      </button>
    </form>

    <p v-if="message" role="status">{{ message }}</p>
  </section>
</template>

<style scoped>
.vat-check {
  max-width: 560px;
  margin: 24px auto;
  padding: 24px;
  background: white;
  border: 1px solid #c6d9ee;
  border-radius: 12px;
}

h2 {
  margin: 0 0 16px;
}

form {
  display: grid;
  gap: 10px;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #a5bcd8;
  border-radius: 7px;
  font: inherit;
}

.vat-check p {
  margin: 16px 0 0;
}
</style>