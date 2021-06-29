<template>
    <a :href="url" target="_blank">{{ proteome_id }}</a>
</template>

<script>
export default {
    props: [
        'proteome_id',
    ],
    computed: {
        url(){
            return `https://www.uniprot.org/proteomes/${ this.proteome_id }`
        }
    }
}
</script>