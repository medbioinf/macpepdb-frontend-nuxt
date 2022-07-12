<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model="sequence" v-on:keyup.enter="digest" class="form-control" type="text" placeholder="Sequence">

                <button @click="digest" :disabled="is_digesting" class="btn btn-primary" type="button" >
                    <i class="fas fa-cut"></i>
                    digest
                </button>
            </div>
        </div>

        <button @click="toggleFilterVisibility()" class="btn btn-primary btn-sm" type="button">
            digest parameters
            <i :class="{'fa-caret-down': !show_filter_inputs, 'fa-caret-up': show_filter_inputs}" class="fas"></i>
        </button>
        <div :class="{show: show_filter_inputs}" class="collapse">
            <p class="mt-2 mb-0">If these parameters are given and valid the sequence is also digested and the resulting peptides are listed in table.</p>
            <div class="row mb-3">
                <label for="maximum-number-of-missed-cleavages" class="col-sm-2 col-form-label">Maximum number of missed cleavages*</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <input v-model.number="digest_params.max_missed_cleavages" id="maximum-number-of-missed-cleavages" class="form-control mb-3" type="number" min="0">
                    <small>
                        <AttributeErrorList v-if="errors.maximum_number_of_missed_cleavages" :errors="errors.maximum_number_of_missed_cleavages"></AttributeErrorList>
                    </small>
                </div>
            </div>

            <div class="row mb-3">
                <label for="minimum-peptide-length" class="col-sm-2 col-form-label">Minimum peptide length*</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <input v-model.number="digest_params.min_length" :max="digest_params.max_length" min="1" id="minimum-peptide-length" class="form-control" type="number">
                    <small>
                        <AttributeErrorList v-if="errors.minimum_peptide_length" :errors="errors.minimum_peptide_length"></AttributeErrorList>
                    </small>
                </div>
            </div>

            <div class="row mb-3">
                <label for="maximum-peptide-length" class="col-sm-2 col-form-label">Maximum peptide length*</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <input v-model.number="digest_params.max_length" :min="digest_params.min_length || 1" id="maximum-peptide-length" class="form-control" type="number" >
                    <small>
                        <AttributeErrorList v-if="errors.maximum_peptide_length" :errors="errors.maximum_peptide_length"></AttributeErrorList>
                    </small>
                </div>
            </div>

            <div class="row mb-3">
                <label for="check-against-database" class="col-sm-2 col-form-label">Link peptides in database</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="checkbox" id="check-against-database" :value="false" v-model="digest_params.link_peptides_in_database">
                    </div>
                </div>
            </div>

        </div>
        
        <div v-if="!is_digesting && peptides.database != null || peptides.digestion != null">
            <p class="mb-0">
                Found {{ database_peptide_length + digestion_peptide_length }} peptide(s).
            </p>
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>
                            Sequence
                        </th>
                        <th colspan="2">
                            Theoretical mass
                        </th>
                    </tr>
                </thead>
                <tbody v-if="peptides.database != null">
                    <tr>
                        <th class="bg-rub-grey" colspan="3">
                            Database peptides
                        </th>
                    </tr>
                    <tr v-for="peptide, idx in peptides.database" :key="peptide.sequence">
                        <th>
                            <NuxtLink :to="{name: 'peptides-sequence', params: {sequence: peptide.sequence}}" target="_blank">{{peptide.sequence}}</NuxtLink>
                        </th>
                        <td>
                            {{ peptide.mass }}
                        </td>
                        <td class="d-flex justify-content-end">
                            <button @click="selectMass(idx, true)" class="btn btn-outline-primary btn-sm">
                                use for theoretical mass search
                                <i class="fas fa-arrow-right"></i>
                            </button>
                        </td>
                    </tr>
                    <tr v-if="peptides.database.length == 0">
                        <td colspan="3">
                            Sequence not found in database.
                        </td>
                    </tr>
                </tbody>
                <tbody>
                    <tr>
                        <th class="bg-rub-grey" colspan="3">
                            Digestion peptides
                        </th>
                    </tr>
                    <tr v-for="peptide, idx in peptides.digestion" :key="peptide.sequence">
                        <th>
                            {{peptide.sequence}}
                        </th>
                        <td>
                            {{ peptide.mass }}
                        </td>
                        <td class="d-flex justify-content-end">
                            <button @click="selectMass(idx, false)" class="btn btn-outline-primary btn-sm">
                                use for theoretical mass search
                                <i class="fas fa-arrow-right"></i>
                            </button>
                        </td>
                    </tr>
                    <tr v-if="database_peptide_length">
                        <td colspan="3">
                            Digestion parameters did not produced any peptides.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <Spinner v-if="is_digesting" class="mt-3 d-flex justify-content-center"></Spinner>
    </div>
</template>


<script>

export default {
    head(){
        return {
            meta: [
                { hid: 'description', name: 'description', content: 'Digest sequences and search results in MaCPepDB' },
                { hid: 'og-desc', name: 'og:desc', content: 'Digest sequences and search results in MaCPepDB' },
                { hid: 'og-title', property: 'og:title', content: `${this.$config.short_title} - Digestion` },
            ]
        }
    },
    data(){
        return {
            // Inputs
            sequence: null,
            digest_params: {
                max_missed_cleavages: 0,
                min_length: 0,
                max_length: 0,
                link_peptides_in_database: false
            },
            // Results
            peptides: {
                // peptides from database
                database: null,
                // peptides from digest
                digestion: null
            },
            errors: {},
            // View
            is_digesting: false,
            show_filter_inputs: false,
        }
    },
    mounted(){
        this.fetchDigestionParameters()
    },
    methods: {
        /**
         * Fetchs the database digestion parameters and places them as default digestion parameters.
         * @function fetchDigestionParameters
         */
        fetchDigestionParameters(){
            fetch(`${this.$config.macpepdb_backend_base_url}/api/dashboard`)
            .then(response => {
                if(response.ok){
                    response.json()
                    .then(response_data => {
                        this.digest_params.max_missed_cleavages = response_data.digestion_paramters.maximum_number_of_missed_cleavages
                        this.digest_params.min_length = response_data.digestion_paramters.minimum_peptide_length
                        this.digest_params.max_length = response_data.digestion_paramters.maximum_peptide_length
                    })
                } else {
                    this.handleUnknownResponse(response)
                } 
            })
        },
        /**
         * Builds the request body for the digestion request.
         * @function buildDigestData
         */
        buildDigestData(){
            return {
                sequence: this.sequence,
                maximum_number_of_missed_cleavages: this.digest_params.max_missed_cleavages,
                minimum_peptide_length: this.digest_params.min_length,
                maximum_peptide_length: this.digest_params.max_length,
                do_database_search: this.digest_params.link_peptides_in_database
            }
        },
        /**
         * Performs/requests the digest.
         * @function digest
         */
        async digest(){
            if(!this.is_digesting){
                this.is_digesting = true
                this.errors = {}
                fetch(`${this.$config.macpepdb_backend_base_url}/api/peptides/digest`, {
                    method: 'POST',
                    cache: 'no-cache',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.buildDigestData())
                }).then(response => {
                    if(response.ok){
                        response.json()
                        .then(response_data => {
                            this.peptides.digestion = response_data.digestion
                            this.peptides.database = this.digest_params.link_peptides_in_database ? response_data.database : null
                        })
                    } else if (response.status == 422) {
                        response.json()
                        .then(response_data => {
                            this.errors = response_data.errors
                        })
                    } else {
                        this.handleUnknownResponse(response)
                    } 
                }).catch(error => {
                })
                .finally(() => {
                    this.is_digesting = false
                })
            }
            return Promise.resolve()
        },
        /**
         * Sends the client to the theoretical mass search with the mass of the peptide peptide.
         * @function selectMass
         * @param {number} idx Index of the peptide.
         * @param {boolean} is_database_peptide Determine if the peptide is in the database list or digestion list.
         */
        selectMass(idx, is_database_peptide){
            var mass = is_database_peptide ? this.peptides.database[idx].mass : this.peptides.digestion[idx].mass
            this.$router.push({ name: "peptides-search", query: { tab: "theoretical-mass-search", theoretical_mass: mass} })
        },
        /**
         * Toggles the visibility of the digestion parameter inputs.
         */
        toggleFilterVisibility(){
            this.show_filter_inputs = !this.show_filter_inputs
        }
    },
    computed: {
        is_digest_params_max_missed_cleavages_valid(){
            return Number.isInteger(this.digest_params.max_missed_cleavages)
                && this.digest_params.max_missed_cleavages >= 0

        },
        is_digest_params_min_length_valid(){
            return Number.isInteger(this.digest_params.min_length)
                && this.digest_params.min_length >= 1

        },
        is_digest_params_max_length_valid(){
            return Number.isInteger(this.digest_params.max_length)
                && this.digest_params.max_length >= this.digest_params.min_length

        },
        is_digest_filter_valid(){
            return this.is_digest_params_max_missed_cleavages_valid
                && this.is_digest_params_min_length_valid
                && this.is_digest_params_max_length_valid
        },
        database_peptide_length(){
            return this.peptides.database != null ? this.peptides.database.length : 0
        },
        digestion_peptide_length(){
            return this.peptides.digest != null ? this.peptides.digestion.length : 0
        }
    }
}
</script>