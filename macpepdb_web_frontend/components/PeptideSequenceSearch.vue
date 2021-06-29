<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model="sequence" v-on:keyup.enter="searchAndDigest" class="form-control" type="text" placeholder="Sequence">

                <button @click="searchAndDigest" :disabled="is_searching || is_digesting" class="btn btn-primary" type="button" >
                    <i class="fas fa-search"></i>
                    search
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
                    <small v-if="Number.isInteger(digest_params.max_missed_cleavages) && !is_digest_params_max_missed_cleavages_valid">
                        <span v-if="!digest_errors.maximum_number_of_missed_cleavages">Must be an integer greater or equals 0.</span>
                        <AttributeErrorList v-if="digest_errors.maximum_number_of_missed_cleavages" :errors="digst_errors.maximum_number_of_missed_cleavages"></AttributeErrorList>
                    </small>
                </div>
            </div>

            <div class="row mb-3">
                <label for="minimum-peptide-length" class="col-sm-2 col-form-label">Minimum peptide length*</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <input v-model.number="digest_params.min_length" :max="digest_params.max_length" min="1" id="minimum-peptide-length" class="form-control" type="number">
                    <small v-if="Number.isInteger(digest_params.min_length) && !is_digest_params_min_length_valid">
                        <span v-if="!digest_errors.minimum_peptide_length">Must be an integer greater or equals 1.</span>
                        <AttributeErrorList v-if="digest_errors.minimum_peptide_length" :errors="digst_errors.minimum_peptide_length"></AttributeErrorList>
                    </small>
                </div>
            </div>

            <div class="row mb-3">
                <label for="maximum-peptide-length" class="col-sm-2 col-form-label">Maximum peptide length*</label>
                <div class="col-sm-10 d-flex flex-column justify-content-center">
                    <input v-model.number="digest_params.max_length" :min="digest_params.min_length || 1" id="maximum-peptide-length" class="form-control" type="number" >
                    <small v-if="Number.isInteger(digest_params.max_length) && !is_digest_params_max_length_valid">
                        <span v-if="!digest_errors.maximum_peptide_length">Must be an integer greater or equals minimum peptide length.</span>
                        <AttributeErrorList v-if="digest_errors.maximum_peptide_length" :errors="digst_errors.maximum_peptide_length"></AttributeErrorList>
                    </small>
                </div>
            </div>
        </div>
        
        <div v-if="peptides.database.length + peptides.digest.length">
            <p class="mb-0">
                Found {{ peptides.database.length + peptides.digest.length }} peptide(s).
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
                <tbody>
                    <tr v-for="peptide, idx in peptides.database" :key="peptide.sequence">
                        <th>
                            <NuxtLink :to="{name: 'peptides-sequence', params: {sequence: peptide.sequence}}" target="_blank">{{peptide.sequence}}</NuxtLink>
                        </th>
                        <td>
                            {{ peptide.mass }}
                        </td>
                        <td class="d-flex justify-content-end">
                            <button @click="selectPeptide(idx, true)" class="btn btn-outline-primary btn-sm">
                                use for theoretical mass search
                                <i class="fas fa-arrow-right"></i>
                            </button>
                        </td>
                    </tr>
                    <tr v-if="peptides.database.length > 0 && peptides.digest.length > 0">
                        <th colspan="3">
                        </th>
                    </tr>
                    <tr v-for="peptide, idx in peptides.digest" :key="peptide.sequence">
                        <th>
                            {{peptide.sequence}}
                        </th>
                        <td>
                            {{ peptide.mass }}
                        </td>
                        <td class="d-flex justify-content-end">
                            <button @click="selectPeptide(idx, false)" class="btn btn-outline-primary btn-sm">
                                use for theoretical mass search
                                <i class="fas fa-arrow-right"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <Spinner v-if="is_searching || is_digesting"></Spinner>
    </div>
</template>


<script>
import Vue from 'vue'

export default {
    props: {
        // Communication bus with parent
        parent_event_bus: {
            type: Vue,
            required: true
        }
    },
    data(){
        return {
            // Inputs
            sequence: null,
            digest_params: {
                max_missed_cleavages: null,
                min_length: null,
                max_length: null
            },
            // Results
            peptides: {
                // peptides from database
                database: [],
                // peptides from digest
                digest: []
            },
            digest_errors: [],
            // View
            is_searching: false,
            is_digesting: false,
            show_filter_inputs: false
        }
    },
    methods: {
        searchAndDigest(){
            this.errors = []
            this.search()
            this.digest()
        },
        async search(event){
            if(!this.is_searching){
                this.is_searching = true
                fetch(`${this.$config.macpepdb_backend_base_url}/api/peptides/${this.sequence}`, {
                    cache: 'no-cache',
                }).then(response => {
                    if(response.ok){
                        return response.json()
                    } else if (response.status == 404) {
                        // Ignore peptide not found
                    } else {
                        this.handleUnknownResponse(response)
                    }
                }).then(response_data => {
                    this.peptides.database = [response_data]
                }).catch(error => {
                })
                .finally(() => {
                    this.is_searching = false
                })
            }
            return Promise.resolve()
        },
        buildDigestData(){
            return {
                sequence: this.sequence,
                maximum_number_of_missed_cleavages: this.digest_params.max_missed_cleavages,
                minimum_peptide_length: this.digest_params.min_length,
                maximum_peptide_length: this.digest_params.max_length
            }
        },
        async digest(){
            if(!this.is_digesting && this.is_digest_filter_valid){
                this.is_digesting = true
                this.digest_errors = {}
                fetch(`${this.$config.macpepdb_backend_base_url}/api/proteins/digest`, {
                    method: 'POST',
                    cache: 'no-cache',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.buildDigestData())
                }).then(response => {
                    if(response.ok){
                        return response.json()
                    } else if (response.status == 422) {
                        response.json()
                        .than(response_body => this.digest_errors = response_body.errors)
                    } else {
                        this.handleUnknownResponse(response)
                    }
                }).then(response_data => {
                    this.peptides.digest = response_data.peptides
                }).catch(error => {
                })
                .finally(() => {
                    this.is_digesting = false
                })
            }
            return Promise.resolve()
        },
        selectPeptide(idx, is_database_peptide){
            // Emit peptide select event to parent if parent event bus is given
            if (this.parent_event_bus){
                var mass = is_database_peptide ? this.peptides.database[idx].mass : this.peptides.digest[idx].mass
                this.parent_event_bus.$emit("MASS_SELECTED", mass)
            }
        },
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
        }
    }
}
</script>