<template>
    <a :href="url" target="_blank">{{ taxonomy_name }} ({{ taxonomy_id }})</a>
</template>

<script>
export default {
    props: [
        'taxonomy_id',
        'taxonomy_name'
    ],
    computed: {
        url(){
            return `https://www.uniprot.org/taxonomy/${ this.taxonomy_id }`
        }
    }
}
</script>