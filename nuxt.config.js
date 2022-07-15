const SHORT_TILE = "MaCPepDB"
const TITLE = "MaCPepDB - Mass Centric Peptide Database"
const DESCRIPTION = "A Database to quickly access all tryptic peptides of the UniProtKB - https://doi.org/10.1021/acs.jproteome.0c00967"


export default {
  // Target: https://go.nuxtjs.dev/config-target
  target: 'server',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: TITLE,
    htmlAttrs: {
      lang: 'en'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' }
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
    "~/plugins/api_error_handling.js",
    "~/plugins/full_url.js",
    "~/plugins/timestamp_to_iso.js"
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
    macpepdb_backend_base_url: process.env.MACPEPDB_BACKEND_BASE_URL || 'http://localhost:3000',
    macpepdb_frontend_base_url: process.env.MACPEPDB_FRONTEND_BASE_URL || 'http://localhost:5000',
    description: DESCRIPTION,
    title: TITLE,
    short_title: SHORT_TILE
  },

  server: {
    host: process.env.MACPEPDB_FRONTEND_INTERFACE || "127.0.0.1",
    port: process.env.MACPEPDB_FRONTEND_PORT || 5000,
    timing: false
  }
}
