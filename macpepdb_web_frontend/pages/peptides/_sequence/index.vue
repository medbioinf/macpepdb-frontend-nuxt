<template>
     <div id="peptide-view">
        <h1>Peptide: {{ this.$route.params.sequence }}</h1>
        <div v-if="!peptide_not_found">
            <div v-if="peptide"> 
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
                                Sequence
                            </th>
                            <td class="text-break">
                                <CodeBlock :code="peptide.sequence" :identifier="'peptide-sequence'" :line_length="60"></CodeBlock>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Theoretical mass
                            </th>
                            <td>
                                {{ peptide.mass }}
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Length
                            </th>
                            <td>
                                {{ peptide.length }}
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Missed cleavages
                            </th>
                            <td>
                                {{ peptide.number_of_missed_cleavages }}
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Taxonomies
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.taxonomy_ids.length">
                                    <li v-for="taxonomy_id in peptide.taxonomy_ids" :key="taxonomy_id">
                                        <UniProtTaxonomyLink :taxonomy_id="taxonomy_id" :taxonomy_name="get_taxonomy_name(taxonomy_id)" />
                                    </li>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Unique in taxonomies
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.unique_taxonomy_ids.length">
                                    <li v-for="taxonomy_id in peptide.unique_taxonomy_ids" :key="taxonomy_id">
                                        <UniProtTaxonomyLink :taxonomy_id="taxonomy_id" :taxonomy_name="get_taxonomy_name(taxonomy_id)" />
                                    </li>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Proteomes IDs
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.proteome_ids.length">
                                    <li v-for="proteome_id in peptide.proteome_ids" :key="proteome_id">
                                        <UniProtProteomeLink :proteome_id="proteome_id" />
                                    </lI>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                SwissProt/TrEMBL
                            </th>
                            <td>
                                <i v-if="peptide.is_swiss_prot" class="fas fa-check"></i>
                                <i v-else class="fas fa-times"></i>
                                /
                                <i v-if="peptide.is_trembl" class="fas fa-check"></i>
                                <i v-else class="fas fa-times"></i>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <h2>Proteins</h2>
                <div v-if="proteins" class="table-responsive-sm">
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
                                    <UniProtTaxonomyLink v-if="taxonomy_map" :taxonomy_id="protein.taxonomy_id" :taxonomy_name="get_taxonomy_name(protein.taxonomy_id)" />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <Spinner v-else class="text-center"></Spinner>
            </div>
            <Spinner v-else class="text-center"></Spinner>
        </div>
        <div v-else>
            Peptide was not found.
        </div>
    </div>
</template>

<script>
export default {
    data(){
        return {
            peptide: null,
            proteins: null,
            taxonomy_map: null,
            peptide_not_found: false
        }
    },
    created(){
        this.get_peptide()
        .then(() => {
            this.get_proteins()
            this.get_taxonomies()
        })
        .catch(error => {
            if(typeof(error) == "number"){
                switch(error){
                    case 404:
                        this.peptide_not_found = true
                }
            }
        })
    },
    methods: {
        async get_peptide(){
            return fetch(`${this.$config.macpepdb_backend_base_url}/api/peptides/${this.$route.params.sequence}`)
            .then(response => {
                if(response.ok){
                    return response.json()
                } else {
                    throw response.status
                }
            })
            .then(response_body => {
                this.peptide = response_body
            })
        },
        async get_proteins(){
            return fetch(`${this.$config.macpepdb_backend_base_url}/api/peptides/${this.$route.params.sequence}/proteins`)
            .then(response => {
                return response.json()
            })
            .then(response_body => {
                this.proteins = response_body.proteins
                return Promise.resolve()
            })
        },
        async get_taxonomies(){
            return fetch(`${this.$config.macpepdb_backend_base_url}/api/taxonomies/by/ids`, {
                "method": 'POST',
                "no-cors": true,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": JSON.stringify({"ids": this.peptide.taxonomy_ids})
            })
            .then(response => {
                return response.json()
            })
            .then(response_body => {
                var taxonomy_map = {}
                response_body.taxonomies.forEach(taxonomy => {
                    taxonomy_map[taxonomy.id] = taxonomy.name
                })
                this.taxonomy_map = taxonomy_map
                return Promise.resolve()
            })
        },
        get_taxonomy_name(taxonomy_id){
            return this.taxonomy_map.hasOwnProperty(taxonomy_id) ? this.taxonomy_map[taxonomy_id] : "";
        }
    }
}
</script>