export default {
  // Target: https://go.nuxtjs.dev/config-target
  target: 'server',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: 'MaCPepDB',
    htmlAttrs: {
      lang: 'en'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'A mass centric peptide database' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    "~/assets/sass/application.sass"
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    "~/plugins/event_bus.js",
    "~/plugins/api_error_handling.js"
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxt/content'
  ],

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
  },

  publicRuntimeConfig: {
    macpepdb_backend_base_url: process.env.MACPEPDB_BACKEND_BASE_URL || 'http://localhost:3000'
  },

  server: {
    host: process.env.MACPEPDB_FRONTEND_INTERFACE || "127.0.0.1",
    port: process.env.MACPEPDB_FRONTEND_PORT || 5000,
    timing: false
  }
}
