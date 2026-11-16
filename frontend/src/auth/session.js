// Shared session state for the whole app (BIZ-32).
// The real session is the HttpOnly cookie; this only remembers who the
// backend says is logged in, so the router and the header can react.

import { readonly, ref } from 'vue'
import { getCurrentUser, login, logout } from '../api/auth'

const user = ref(null)
let loaded = false

export const currentUser = readonly(user)

// Ask the backend who is logged in. Uses the cached answer unless `force`.
// If the server cannot be reached, the user is treated as logged out and the
// next call asks again.
export async function loadSession({ force = false } = {}) {
  if (force || !loaded) {
    try {
      user.value = await getCurrentUser()
      loaded = true
    } catch {
      user.value = null
    }
  }
  return user.value
}

export async function signIn(email, password) {
  user.value = await login(email, password)
  loaded = true
  return user.value
}

// Ends the session on the backend (clears the cookie) and forgets the user.
// The user is forgotten even if the request fails, so the UI never keeps
// showing a logged-in state after "Log out"; protected pages still ask the
// backend before opening.
export async function signOut() {
  try {
    await logout()
  } catch {
    // Ignored on purpose, see above.
  } finally {
    user.value = null
    loaded = false
  }
}
