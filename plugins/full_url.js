export default (context, inject) => {
    inject('full_url', () => `${context.$config.macpepdb_frontend_base_url}${context.route.fullPath}`)
}