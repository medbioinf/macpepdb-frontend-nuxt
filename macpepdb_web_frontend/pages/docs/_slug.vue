<template>
    <div>
        <h1>{{ article.title }}</h1>
        <p>{{ article.description }}</p>
        <nav>
            <ul>
                <li v-for="link of article.toc" :key="link.id">
                    <NuxtLink :to="`#${link.id}`">{{ link.text }}</NuxtLink>
                </li>
            </ul>
        </nav>
        <article>
            <nuxt-content :document="article"></nuxt-content>
        </article>
    </div>
</template>

<script>
export default {
    async asyncData({ $content, params }) {
        const article = await $content('docs', params.slug).fetch()
        return { article }
    }
}
</script>