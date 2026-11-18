<script setup>
import { ref } from 'vue'
import { request } from './api/auth'

const vatNumber = ref('')
const checking = ref(false)
const error = ref('')
const result = ref(null)

function clearMessages() {
  error.value = ''
  result.value = null
}

function sourceDescription(source) {
  if (source.status === 'checked') {
    return source.valid ? 'Checked · Valid VAT number' : 'Checked · VAT number not valid'
  }
  if (source.status === 'unavailable') {
    return 'Unavailable · Try again later'
  }
  return 'Not yet implemented'
}

async function checkPartner() {
  if (checking.value) return
  clearMessages()

  const identifier = vatNumber.value.replace(/\s/g, '').toUpperCase()
  if (!identifier) {
    error.value = 'Enter a VAT / UID number.'
    return
  }
  if (!/^ATU[0-9]{8}$/.test(identifier)) {
    error.value = 'Enter ATU followed by eight digits, for example ATU12345678.'
    return
  }

  checking.value = true
  try {
    result.value = await request('/partner-check', {
      method: 'POST',
      body: JSON.stringify({ identifier }),
    })
  } catch (err) {
    error.value = err.status === 401
      ? 'Your session has expired. Log in again to run a check.'
      : err.message
  } finally {
    checking.value = false
  }
}
</script>

<template>
  <section class="vat-check" aria-labelledby="partner-check-title">
    <h2 id="partner-check-title">Check a business partner</h2>

    <form @submit.prevent="checkPartner">
      <label for="vat-number">Austrian VAT / UID number</label>
      <input
        id="vat-number"
        v-model="vatNumber"
        type="text"
        placeholder="ATU12345678"
        autocomplete="off"
        aria-required="true"
        :disabled="checking"
        @input="clearMessages"
      />
      <button class="button" type="submit" :disabled="checking">
        {{ checking ? 'Checking…' : 'Run check' }}
      </button>
    </form>

    <p v-if="checking" role="status">Checking VIES. This may take a few seconds.</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div v-if="result" class="results" role="status">
      <h3>Results for {{ result.identifier }}</h3>
      <dl>
        <div v-for="source in result.sources" :key="source.name" class="source">
          <dt>{{ source.name }}</dt>
          <dd>{{ sourceDescription(source) }}</dd>
        </div>
      </dl>
    </div>
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

form, dl {
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

.results, .vat-check p {
  margin: 16px 0 0;
}

.error {
  color: #8a1c1c;
}

.source {
  padding-top: 10px;
  border-top: 1px solid #c6d9ee;
}

dt {
  font-weight: 600;
}

dd {
  margin: 2px 0 0;
}
</style>
