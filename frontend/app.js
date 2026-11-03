/*
 * BizPartnerCheck — frontend logic (plain JavaScript, no build step).
 *
 * Sections:
 *   1. BACKEND ....... API base URL and auth routes (edit here)
 *   2. AUTH API ...... the only place where auth requests are made
 *   3. VALIDATION .... required fields and email format
 *   4. UI HELPERS .... field errors, alerts, loading button
 *   5. PAGES ......... register and login form behaviour
 *   6. START ......... runs the code for the current page
 */
'use strict';

/* ==========================================================================
   1. BACKEND
   --------------------------------------------------------------------------
   PROVISIONAL: the backend auth endpoints do not exist yet. The URL, routes,
   request bodies and status codes below are placeholders, not an agreed
   contract, and the connection has not been verified. Update them when the
   backend defines the auth API.
   ========================================================================== */

// PROVISIONAL — base URL of the backend REST API (FastAPI), without trailing slash.
const API_BASE_URL = 'http://localhost:8000';

// PROVISIONAL — auth routes, relative to API_BASE_URL.
const REGISTER_PATH = '/auth/register';
const LOGIN_PATH = '/auth/login';

/* ==========================================================================
   2. AUTH API
   ========================================================================== */

// Error kinds the pages know how to display.
const AUTH_ERROR = {
  NETWORK: 'network', // the server could not be reached
  INVALID_CREDENTIALS: 'invalid-credentials', // login rejected
  REGISTRATION: 'registration', // registration rejected
  UNEXPECTED: 'unexpected', // anything else
};

class AuthError extends Error {
  constructor(kind, message) {
    super(message);
    this.name = 'AuthError';
    this.kind = kind;
  }
}

async function postJson(path, body) {
  try {
    return await fetch(API_BASE_URL + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch {
    // fetch only fails like this when there is no response at all
    // (server down, wrong URL, CORS blocked, no internet).
    throw new AuthError(AUTH_ERROR.NETWORK, 'Could not reach the server');
  }
}

/**
 * Registers a user. data = { email, firstName, lastName, organizationNumber }
 * PROVISIONAL: body field names and status handling must match the backend.
 */
async function register(data) {
  const response = await postJson(REGISTER_PATH, data);
  if (!response.ok) {
    throw new AuthError(AUTH_ERROR.REGISTRATION, 'Registration failed (HTTP ' + response.status + ')');
  }
}

/**
 * Logs a user in. data = { email, password }
 * PROVISIONAL: assumes HTTP 401 means incorrect credentials. Session/token
 * handling is not implemented yet.
 */
async function login(data) {
  const response = await postJson(LOGIN_PATH, data);
  if (response.status === 401) {
    throw new AuthError(AUTH_ERROR.INVALID_CREDENTIALS, 'Invalid email or password');
  }
  if (!response.ok) {
    throw new AuthError(AUTH_ERROR.UNEXPECTED, 'Login failed (HTTP ' + response.status + ')');
  }
}

/** Text shown to the user for each error kind. */
function getErrorMessage(error) {
  const messages = {
    [AUTH_ERROR.NETWORK]:
      'Unable to connect to the server. Please check your connection and try again.',
    [AUTH_ERROR.INVALID_CREDENTIALS]: 'Incorrect email or password.',
    [AUTH_ERROR.REGISTRATION]:
      'Registration could not be completed. Please check your details and try again.',
    [AUTH_ERROR.UNEXPECTED]: 'Something went wrong. Please try again later.',
  };
  const kind = error instanceof AuthError ? error.kind : AUTH_ERROR.UNEXPECTED;
  return messages[kind];
}

/* ==========================================================================
   3. VALIDATION
   ========================================================================== */

// Simple, permissive email check: something@something.tld without spaces.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateRequired(value, label) {
  return value.trim() === '' ? label + ' is required.' : '';
}

function validateEmail(value) {
  const required = validateRequired(value, 'Email');
  if (required) return required;
  return EMAIL_PATTERN.test(value.trim()) ? '' : 'Enter a valid email address.';
}

/* ==========================================================================
   4. UI HELPERS
   ========================================================================== */

function showFieldError(input, message) {
  const errorElement = document.getElementById(input.id + '-error');
  if (message) {
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', errorElement.id);
    errorElement.textContent = message;
    errorElement.hidden = false;
  } else {
    input.removeAttribute('aria-invalid');
    input.removeAttribute('aria-describedby');
    errorElement.textContent = '';
    errorElement.hidden = true;
  }
}

/**
 * Validates the inputs of a form. rules = { inputName: (value) => errorText }.
 * Shows each error under its field and returns true if everything is valid.
 */
function validateForm(form, rules) {
  let firstInvalid = null;
  for (const [name, rule] of Object.entries(rules)) {
    const input = form.elements[name];
    const message = rule(input.value);
    showFieldError(input, message);
    if (message && !firstInvalid) firstInvalid = input;
  }
  if (firstInvalid) firstInvalid.focus();
  return firstInvalid === null;
}

/** Clears a field's error as soon as the user types in it. */
function clearErrorsOnInput(form) {
  form.querySelectorAll('input').forEach((input) => {
    input.addEventListener('input', () => showFieldError(input, ''));
  });
}

function showAlert(alertElement, title, message) {
  alertElement.querySelector('.alert-title').textContent = title;
  alertElement.querySelector('.alert-body').textContent = message;
  alertElement.hidden = false;
}

function hideAlert(alertElement) {
  alertElement.hidden = true;
}

/** Waiting state: disables the form and shows "Loading…" in the button. */
function setLoading(form, loading) {
  const fieldset = form.querySelector('fieldset');
  const button = form.querySelector('button[type="submit"]');
  fieldset.disabled = loading;
  if (loading) {
    button.dataset.label = button.textContent;
    button.innerHTML = '<span class="spinner" aria-hidden="true"></span>Loading…';
    button.setAttribute('aria-busy', 'true');
  } else {
    button.textContent = button.dataset.label || button.textContent;
    button.removeAttribute('aria-busy');
  }
}

/* ==========================================================================
   5. PAGES
   ========================================================================== */

function initRegisterPage() {
  const form = document.getElementById('register-form');
  const alertElement = document.getElementById('register-alert');
  const formView = document.getElementById('register-view');
  const successView = document.getElementById('register-success');

  clearErrorsOnInput(form);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert(alertElement);

    const valid = validateForm(form, {
      email: validateEmail,
      firstName: (value) => validateRequired(value, 'First name'),
      lastName: (value) => validateRequired(value, 'Last name'),
      organizationNumber: (value) => validateRequired(value, 'Organization number'),
    });
    if (!valid) return;

    const data = {
      email: form.elements.email.value.trim(),
      firstName: form.elements.firstName.value.trim(),
      lastName: form.elements.lastName.value.trim(),
      organizationNumber: form.elements.organizationNumber.value.trim(),
    };

    setLoading(form, true);
    try {
      await register(data);
      document.getElementById('registered-email').textContent = data.email;
      formView.hidden = true;
      successView.hidden = false;
    } catch (error) {
      const kind = error instanceof AuthError ? error.kind : AUTH_ERROR.UNEXPECTED;
      const title = kind === AUTH_ERROR.NETWORK ? 'Connection problem' : 'Registration failed';
      showAlert(alertElement, title, getErrorMessage(error));
    } finally {
      setLoading(form, false);
    }
  });
}

function initLoginPage() {
  const form = document.getElementById('login-form');
  const alertElement = document.getElementById('login-alert');
  const formView = document.getElementById('login-view');
  const successView = document.getElementById('login-success');

  clearErrorsOnInput(form);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    hideAlert(alertElement);

    const valid = validateForm(form, {
      email: validateEmail,
      password: (value) => validateRequired(value, 'Password'),
    });
    if (!valid) return;

    setLoading(form, true);
    try {
      await login({
        email: form.elements.email.value.trim(),
        password: form.elements.password.value,
      });
      formView.hidden = true;
      successView.hidden = false;
    } catch (error) {
      const kind = error instanceof AuthError ? error.kind : AUTH_ERROR.UNEXPECTED;
      const title = kind === AUTH_ERROR.NETWORK ? 'Connection problem' : 'Login failed';
      showAlert(alertElement, title, getErrorMessage(error));
      if (kind === AUTH_ERROR.INVALID_CREDENTIALS) form.elements.password.value = '';
    } finally {
      setLoading(form, false);
    }
  });
}

/* ==========================================================================
   6. START
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  if (page === 'register') initRegisterPage();
  if (page === 'login') initLoginPage();

  document.querySelectorAll('[data-year]').forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });
});
