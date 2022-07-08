<template>
    <div class="table-responsive-sm">
        <table class="table">
            <thead>
                <tr>
                    <th>
                        Accession
                    </th>
                    <th>
                        Proteinname
                    </th>
                    <th>
                        Taxonomy
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="protein in proteins" :key="protein.accession">
                    <th>
                        <NuxtLink :to="{name: 'proteins-accession', params: {accession: protein.accession}}">{{ protein.accession }}</NuxtLink>
                    </th>
                    <td>
                        {{ protein.name }}
                    </td>
                    <td>
                        <UniProtTaxonomyLink :taxonomy_id="protein.taxonomy_id" :taxonomy_name="taxonomy_map[protein.taxonomy_id] || ''" />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
export default {
    props: {
        proteins: {
            type: Array,
            required: true
        },
        taxonomy_map: {
            type: Object,
            required: true
        }
    }
}
</script>