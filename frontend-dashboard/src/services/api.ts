import axios from "axios";

// N-D1/N-D16: how a client reaches the backend was previously hardcoded to
// `http://127.0.0.1:8000` in three places that had drifted apart, and the
// service layer then called unversioned paths (`/verdicts`) against a backend
// that serves everything under `/api/v2` -- so each request 404'd, which
// presented as an empty dashboard rather than as an error.
//
// Both values are build-time env vars (Vite inlines `import.meta.env.*` at
// build time) with a dev-only fallback, so a deployed bundle points wherever
// `VITE_API_BASE_URL` says instead of at the build machine's localhost.
const DEV_API_BASE_URL = "http://127.0.0.1:8000/api/v2";

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? DEV_API_BASE_URL;

// `wss://` when the page itself is served over TLS, otherwise `ws://`. A
// browser blocks a plaintext `ws://` from an `https://` page, so deriving this
// rather than hardcoding it is what makes a deployed dashboard connect.
const DEV_WS_URL = "ws://127.0.0.1:8000/ws/verdicts";

export const WS_URL: string =
  import.meta.env.VITE_WS_URL ??
  (window.location.protocol === "https:"
    ? DEV_WS_URL.replace("ws://", "wss://")
    : DEV_WS_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Automatically attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
