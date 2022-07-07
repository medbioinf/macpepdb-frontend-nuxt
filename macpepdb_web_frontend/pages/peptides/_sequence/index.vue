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
                    </tbody>
                    <tbody v-if="peptide.metadata">
                        <tr>
                            <th>
                                Proteomes IDs
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.metadata.proteome_ids.length">
                                    <li v-for="proteome_id in peptide.metadata.proteome_ids" :key="proteome_id">
                                        <UniProtProteomeLink :proteome_id="proteome_id" />
                                    </lI>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Taxonomies
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.metadata.taxonomy_ids.length">
                                    <li v-for="taxonomy_id in peptide.metadata.taxonomy_ids" :key="taxonomy_id">
                                        <UniProtTaxonomyLink :taxonomy_id="taxonomy_id" :taxonomy_name="taxonomy_map[taxonomy_id] || ''" />
                                    </li>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                Unique in taxonomies
                            </th>
                            <td>
                                <RetractableList v-if="taxonomy_map" :number_of_elements="peptide.metadata.unique_taxonomy_ids.length">
                                    <li v-for="taxonomy_id in peptide.metadata.unique_taxonomy_ids" :key="taxonomy_id">
                                        <UniProtTaxonomyLink :taxonomy_id="taxonomy_id" :taxonomy_name="taxonomy_map[taxonomy_id] || ''" />
                                    </li>
                                </RetractableList>
                            </td>
                        </tr>
                        <tr>
                            <th>
                                SwissProt/TrEMBL
                            </th>
                            <td>
                                <i v-if="peptide.metadata.is_swiss_prot" class="fas fa-check"></i>
                                <i v-else class="fas fa-times"></i>
                                /
                                <i v-if="peptide.metadata.is_trembl" class="fas fa-check"></i>
                                <i v-else class="fas fa-times"></i>
                            </td>
                        </tr>
                    </tbody>
                    <tbody v-else>
                        <tr>
                            <th colspan="2">
                                Metadata missing
                            </th>
                        </tr>
                    </tbody>
                </table>

                <h2>Reviewed proteins</h2>
                <ProteinTable v-if="reviewed_proteins != null && taxonomy_map != null" :proteins="reviewed_proteins" :taxonomy_map="taxonomy_map"></ProteinTable>

                <button @click="toggle_unreviewed_proteins_visibility" type="button" class="btn btn-primary btn-sm">
                    <span class="me-2">Unreviewed proteins</span>
                    <i :class="{'fa-caret-up': show_unreviewed_proteins, 'fa-caret-down': !show_unreviewed_proteins}" class="fas"></i>
                </button>
                <div :class="{show: show_unreviewed_proteins}" class="collapse">
                    <h2>Uneviewed proteins</h2>
                    <ProteinTable v-if="unreviewed_proteins != null && taxonomy_map != null" :proteins="unreviewed_proteins" :taxonomy_map="taxonomy_map"></ProteinTable>
                </div>
                <Spinner v-if="!are_proteins_loaded" class="text-center"></Spinner>
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
            reviewed_proteins: null,
            unreviewed_proteins: null,
            taxonomy_map: null,
            peptide_not_found: false,
            show_unreviewed_proteins: false
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
                this.reviewed_proteins = response_body.reviewed_proteins
                this.unreviewed_proteins = response_body.unreviewed_proteins
                return Promise.resolve()
            })
        },
        async get_taxonomies(){
            if(this.peptide.metadata != null){
                return fetch(`${this.$config.macpepdb_backend_base_url}/api/taxonomies/by/ids`, {
                    "method": 'POST',
                    "no-cors": true,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": JSON.stringify({"ids": this.peptide.metadata.taxonomy_ids})
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
            }
        },
        toggle_unreviewed_proteins_visibility(){
            this.show_unreviewed_proteins = !this.show_unreviewed_proteins
        }
    },
    computed: {
        are_proteins_loaded(){
            return this.reviewed_proteins != null && this.unreviewed_proteins != null
        }
    }
}
</script>