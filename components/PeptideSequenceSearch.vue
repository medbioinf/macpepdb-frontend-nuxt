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
                        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="swiss-prot-and-trembl" :value="null" v-model="search_params.is_reviewed">
                        <label class="form-check-label" for="swiss-prot-and-trembl">Both</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="swiss-prot-only" :value="true" v-model="search_params.is_reviewed">
                        <label class="form-check-label" for="swiss-prot-only">Swiss-Prot</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="trembl-only" :value="false" v-model="search_params.is_reviewed">
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
            errors: {}
        }
    },
    methods: {
        search(){
            if(!this.is_searching){
                this.is_searching = true
                var search_url = `${this.$config.macpepdb_backend_base_url}/api/peptides/${this.sequence}`
                if(this.search_params.is_reviewed != null)
                {
                    search_url += "?is_reviewed="
                    search_url += this.search_params.is_reviewed ? "1" : "0"
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
                        response.json().then(response_data => {
                            this.errors = response_data.errors
                        })
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