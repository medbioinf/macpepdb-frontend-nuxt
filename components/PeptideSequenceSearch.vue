<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model="sequence" v-on:keyup.enter="search" :disabled="is_searching" class="form-control" type="text" placeholder="Sequence">

                <button @click="search" class="btn btn-primary" type="button" >
                    <i class="fas fa-search"></i>
                    search
                </button>
            </div>
        </div>
        <button @click="toggleFilterVisibility()" class="btn btn-primary btn-sm" type="button">
            filter
            <i :class="{'fa-caret-down': !show_filters, 'fa-caret-up': show_filters}" class="fas"></i>
        </button>
        <div :class="{show: show_filters}" class="collapse">
            <div class="row mb-3">
                <div class="col-sm-2 col-form-label">Uniprot Database</div>
                <div class="col-sm-10 d-flex align-items-center">
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sequence-search-review-filter" id="swiss-prot-and-trembl" :value="null" v-model="search_params.is_reviewed">
                        <label class="form-check-label" for="swiss-prot-and-trembl">Both</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sequence-search-review-filter" id="swiss-prot-only" :value="1" v-model="search_params.is_reviewed">
                        <label class="form-check-label" for="swiss-prot-only">Swiss-Prot</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="sequence-search-review-filter" id="trembl-only" :value="0" v-model="search_params.is_reviewed">
                        <label class="form-check-label" for="trembl-only">TrEMBL</label>
                    </div>
                </div>
            </div>
        </div>
        <table v-if="peptide" class="table">
            <thead>
                <tr>
                    <th>
                        Sequence
                    </th>
                    <th>
                        Theoretical mass
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th>
                        <NuxtLink :to="{name: 'peptides-sequence', params: {sequence: peptide.sequence}}">{{peptide.sequence}}</NuxtLink>
                    </th>
                    <td>
                        {{ peptide.mass }}
                    </td>
                </tr>
            </tbody>
        </table>
        <div v-if="not_found">
            <p>
                Peptide not found.
            </p>
        </div>
    </div>
</template>


<script>
export default {
    data(){
        return {
            // Inputs
            sequence: null,
            show_filters: false,
            search_params: {
                is_reviewed: null
            },
            is_searching: false,
            peptide: null,
            not_found: false
        }
    },
    methods: {
        search(){
            if(!this.is_searching){
                this.is_searching = true
                this.not_found = false
                var search_url = `${this.$config.macpepdb_backend_base_url}/api/peptides/${this.sequence}`
                if(this.search_params.is_reviewed != null){
                    search_url += `?is_reviewed=${this.search_params.is_reviewed}`
                }
                fetch(search_url, {
                    method: 'GET',
                    cache: 'no-cache',
                }).then(response => {
                    if(response.ok) {
                        response.json().then(response_data => {
                            this.peptide = response_data
                        })
                    } else if(response.status == 404) {
                        this.not_found = true
                        this.peptide = null
                    } else {
                        this.handleUnknownResponse(response)
                    }
                }).finally(() => {
                    this.is_searching = false
                })
            }
        },
        toggleFilterVisibility(){
            this.show_filters = !this.show_filters
        }
    }
}
</script>