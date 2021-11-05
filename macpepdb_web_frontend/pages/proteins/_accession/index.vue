<template>
    <div id="protein-view">
        <div v-if="protein">
            <h1>Protein: {{ protein.accession }}</h1>
            <table class="table">
                <thead>
                    <tr>
                        <th>
                            Attribute
                        </th>
                        <th>
                            Value
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>
                            Accession
                        </th>
                        <td>
                            {{ protein.accession }}
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Name
                        </th>
                        <td>
                            {{ protein.name }}
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Taxonomy
                        </th>
                        <td>
                            <UniProtTaxonomyLink :taxonomy_id="protein.taxonomy_id" :taxonomy_name="protein.taxonomy_name" />
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Proteome ID
                        </th>
                        <td>
                            <div v-if="protein.proteome_id">
                                <UniProtProteomeLink :proteome_id="protein.proteome_id" />
                            </div>
                            <div v-else>
                                not available
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Review status
                        </th>
                        <td>
                            <span v-if="protein.is_reviewed">
                                is reviewed
                            </span>
                            <span v-else>
                                not reviewed
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Sequence
                        </th>
                        <td class="text-break">
                            <CodeBlock :code="protein.sequence" identifier="protein-sequence" :line_length="60"></CodeBlock>
                        </td>
                    </tr>
                    <tr>
                        <th>
                            Uniprot
                        </th>
                        <td>
                            <a class="text-wrap-anywhere" :href="uniprot_url" target="_blank">{{uniprot_url}}</a>
                        </td>
                    </tr>
                </tbody>
            </table>

            <h2>Peptides</h2>
            <FilterableProteinPeptidesList v-if="protein" :protein_accession="protein.accession"></FilterableProteinPeptidesList>
        </div>
        <div v-if="protein == null && !is_searching">
            <p>
                Protein not found.
            </p>
        </div>
        <Spinner v-if="is_searching" class="text-center"></Spinner>
    </div>
</template>

<script>
export default {
    data(){
        return {
            protein: null,
            peptides: null,
            is_searching: true
        }
    },
    created(){
        fetch(`${this.$config.macpepdb_backend_base_url}/api/proteins/${this.$route.params.accession}`)
        .then(response => {
            if(response.ok){
                response.json()
                .then(response_body => {
                    this.protein = response_body
                })
            } else if(response.status == 404) {
                // Protein not found, do nothing
            } else {
                this.handleUnknownResponse(response)
            }
        })
        .finally(() => {
            this.is_searching = false
        })
    },
    mounted(){
        this.$event_bus.$on(this.peptides_page_change_event, page => {
            this.current_page = page
            this.loadPeptides()
        })
    },
    computed: {
        uniprot_url(){
            return `https://www.uniprot.org/uniprot/${this.protein.accession}`
        }
    }
}
</script>