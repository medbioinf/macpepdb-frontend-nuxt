<template>
    <main class="container-fluid mr-0">
        <div class="row application-content-row">
            <nav :class="{'extended-menu': show_menu}" class="col-12 col-lg-2 position-sticky d-flex flex-column py-3 application-nav-column collapsed-menu">
                <div class="d-flex justify-content-between align-items-center">
                    <h1 class="brand text-break">
                        <NuxtLink to="/">
                            MaCPepDB
                        </NuxtLink>
                    </h1>
                    <button @click="toggleMenu" type="button" class="btn btn-sm btn-outline-primary d-lg-none">
                        <i :class="{'fa-times': show_menu, 'fa-bars': !show_menu}" class="fas"></i>
                    </button>
                </div>
                <nav class="d-flex flex-column flex-fill application-menu ">
                    <div class="flex-fill">
                        <p class="application-menu-label">
                                Explore the database
                        </p>
                        <ul class="nav flex-column">
                                <li class="nav-item">
                                        <NuxtLink to="/proteins/search" class="nav-link">
                                                <i class="fas fa-search"></i>
                                                <span>Start with proteins</span>
                                        </NuxtLink>
                                </li>
                                <li class="nav-item">
                                        <NuxtLink to="/peptides/search" class="nav-link">
                                                <i class="fas fa-search"></i>
                                                <span>Start with peptide</span>
                                        </NuxtLink>
                                </li>
                        </ul>
                        <p class="application-menu-label">
                                Tools
                        </p>
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <NuxtLink to="/digestion" class="nav-link">
                                        <i class="fas fa-cut"></i>
                                        <span>Digestion</span>
                                </NuxtLink>
                            </li>
                        </ul>
                        <p class="application-menu-label">
                        </p>
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <NuxtLink to="/publications_and_posters" class="nav-link">
                                    <i class="fas fa-book"></i>
                                    <span>Publications & Posters</span>
                                </NuxtLink>
                            </li>
                            <li class="nav-item">
                                <NuxtLink to="/docs" class="nav-link">
                                    <i class="fas fa-file-code"></i>
                                    <span>Documentation</span>
                                </NuxtLink>
                            </li>
                        </ul>
                    </div>
                    <ul class="nav flex-column justify-content-end">
                        <li class="nav-item">
                            <NuxtLink to="/errors" class="nav-link">
                                <i class="fas fa-exclamation-circle"></i>
                                <span>Errors</span>
                                <span v-if="$store.state.errors.errors.length" class="badge badge-pill bg-danger">{{ $store.state.errors.errors.length }}</span>
                            </NuxtLink>
                        </li>
                    </ul>
                    <div class="external-pages-menu">
                        <ul class="nav flex-column">
                            <li><a href="https://www.ruhr-uni-bochum.de/de/impressum" target="_blank">Legal information</a></li>
                            <li><a href="https://www.ruhr-uni-bochum.de/de/datenschutz" target="_blank">Privacy</a></li>
                        </ul>
                        <div class="sponsors-logos">
                            <a href="https://www.ruhr-uni-bochum.de" target="_blank"><img class="w-25" src="~/assets/images/rub-logo-small.png" alt="Logo of the Ruhr University Bochum"/></a>
                            <a href="https://www.ruhr-uni-bochum.de/mpc/" target="_blank"><img class="w-25" src="~/assets/images/mpc-logo-small.png" alt="Logo of the Medical Proteom Center"/></a>
                        </div>
                    </div>
                </nav>
            </nav>
            <div class="col-12 col-lg-10">
                <div class="container-fluid py-3">
                    <div class="content">
                        <Nuxt keep-alive />
                    </div>
                </div>
            </div>
        </div>
    </main>
</template>

<script>
import logo_wide_png from "~/assets/images/logo-wide.png"

export default {
    head(){
        return {
            meta: [
                { hid: 'description', name: 'description', content: this.$config.DESCRIPTION },
                { hid: 'og-type', property: 'og:type', content: 'website' },
                { hid: 'og-url', property: 'og:url', content: this.$full_url },
                { hid: 'og-title', property: 'og:title', content: this.$config.title },
                { hid: 'og-site_name', name: 'og:site_name ', content: this.$config.short_title },
                { hid: 'og-desc', name: 'og:desc', content: this.$config.description },
                { hid: 'og-image', property: 'og:image', content: logo_wide_png },
                { hid: 'og-image-type', property: 'og:image:type', content: 'image/png' },
                { hid: 'og-image-width', property: 'og:image:width', content: 698 },
                { hid: 'og-image-height', property: 'og:image:height', content: 400 },
                { hid: 'twitter-card', name: 'twitter:card', content: 'summary' }
            ]
        }
    },
    data(){
        return {
            show_menu: false
        }
    },
    methods: {
        toggleMenu(){
            this.show_menu = !this.show_menu
        }
    }
}
</script>

<style>
</style>
