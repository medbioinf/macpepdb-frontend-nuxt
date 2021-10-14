<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model.number="search_params.mass" v-on:keyup.enter="search" class="form-control" type="text" placeholder="Theoretical mass">
                <button @click="search()" :disabled="is_searching" class="btn btn-primary">
                    <i class="fas fa-search"></i>
                    search
                </button>
            </div>
            <small v-if="errors.precursor">
                <AttributeErrorList :errors="errors.precursor"></AttributeErrorList>
            </small>
        </div>
        <button @click="toggleFilterVisibility()" class="btn btn-primary btn-sm" type="button">
            filter
            <i :class="{'fa-caret-down': !show_filter_inputs, 'fa-caret-up': show_filter_inputs}" class="fas"></i>
        </button>
        <div :class="{show: show_filter_inputs}" class="collapse">
            <MassToleranceFilter :parent_event_bus="local_event_bus" :inital_lower_tolerance="search_params.mass_tolerance.lower" :inital_upper_tolerance="search_params.mass_tolerance.upper" :errors="errors"></MassToleranceFilter>
            <TaxonomyFilter :parent_event_bus="local_event_bus"></TaxonomyFilter>
            <ModificationFilter :parent_event_bus="local_event_bus" :modifications="search_params.modifications" :errors="errors"></ModificationFilter>

            <div id="result-order">
                <div id="search-for" class="divider">Result order</div>

                <div class="row mb-3">
                    <label for="order-by" class="col-sm-2 col-form-label">Order by</label>
                    <div class="col-sm-10 d-flex align-items-center">
                        <select id="order-by" class="form-select" v-model="search_params.order.by">
                            <option value="mass">Mass</option>
                            <option value="length">Length</option>
                            <option value="sequence">Sequence</option>
                            <option value="number_of_missed_cleavages">Missed cleavages</option>
                        </select>
                    </div>
                </div>

                <div class="row mb-3">
                    <label for="order-by" class="col-sm-2 col-form-label">Order direction</label>
                    <div class="col-sm-10 d-flex align-items-center">
                        <select class="form-select" v-model="search_params.order.direction">
                            <option value="asc">Ascending</option>
                            <option value="desc">Descending</option>
                        </select>
                    </div>
                </div>
            </div>

            <div id="additional-filter">
                <div id="search-for" class="divider">Additional filter</div>

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
        </div>

        <div class="peptides">
            <div v-if="results.peptides">
                <div class="d-flex justify-content-between align-items-center">
                    <p class="mb-0">
                        Found {{ results.total_count }} peptide(s).
                    </p>
                    <!-- File downloads with JS is a bit tricky and not very elegant. For the CSV download we use a classic form and put the search parameter as JSON-string into a hidden input field --> 
                    <form v-if="results.peptides.length" :action="`${this.$config.macpepdb_backend_base_url}/api/peptides/search.csv`" method="post">
                        <button type="submit" class="btn btn-primary btn-sm">
                            download as CSV (Excel compatible)
                            <i class="fas fa-download"></i>
                        </button>
                        <input :value="download_search_params" name="search_params" type="hidden">
                    </form>
                </div>
                <table class="table">
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
                        <tr v-for="peptide in results.peptides" :key="peptide.sequence">
                            <th>
                                <NuxtLink :to="{name: 'peptides-sequence', params: {sequence: peptide.sequence}}">{{peptide.sequence}}</NuxtLink>
                            </th>
                            <td>
                                {{ peptide.mass }}
                            </td>
                        </tr>
                    </tbody>
                </table>

                <Pagination :parent_event_bus="local_event_bus" :total_items="results.total_count" :items_per_page="peptides_per_page"></Pagination>
            </div>
        </div>
        <div v-if="errors.length" id="search-errors" class="alert alert-danger fade show" role="alert">
            <ul class="mb-0">
                <li v-for="error in errors" :key="error">{{ error }}</li>
            </ul>
        </div>
        <Spinner v-if="is_searching" class="text-center"></Spinner>
    </div>
</template>


<script>
import Vue from 'vue'

const PEPTIDES_PER_PAGE = 100

export default {
    props: {
        // Mass which is passed from parent
        parent_mass: {
            type: Number,
            required: false,
            default: 0
        }
    },
    data(){
        return {
            // Component communication
            local_event_bus: new Vue(),
            // View
            show_filter_inputs: false,
            // Search
            search_params: {
                mass: null,
                mass_tolerance: {
                    lower: null,
                    upper: null
                },
                max_missed_cleavages: null,
                max_variable_modifications: null,
                modifications: [],
                taxonomy_id: null,
                order: {
                    by: "mass",
                    direction: "asc"
                },
                is_reviewed: null,
            },
            is_searching: false,
            is_downloading: false,
            last_search_parameter: "",
            errors: {},
            // Results
            results: {
                peptides: null,
                total_count: null
            },
            total_peptide_count: 0,
            // Pagination
            current_result_page: 1
        }
    },
    mounted(){
        // Mass tolerance filter events
        this.local_event_bus.$on("LOWER_TOLERANCE_CHANGED", tolerance => this.search_params.mass_tolerance.lower = tolerance )
        this.local_event_bus.$on("UPPER_TOLERANCE_CHANGED", tolerance => this.search_params.mass_tolerance.upper = tolerance )
        // Modifiation filter events
        this.local_event_bus.$on("MODIFICATION_ADDED", modification => this.search_params.modifications.push(modification) )
        this.local_event_bus.$on("MODIFICATION_REMOVED", modification_idx => this.search_params.modifications.splice(modification_idx, 1) )
        this.local_event_bus.$on("MAX_VARIABLE_MODIFICATION_CHANAGED", max_variable_modifications => this.search_params.max_variable_modifications = max_variable_modifications )
        // Taxonomy filter events
        this.local_event_bus.$on("TAXONOMY_SELECTED", taxonomy => { this.search_params.taxonomy_id = taxonomy.id })
        this.local_event_bus.$on("TAXONOMY_UNSELECTED", () => { this.search_params.taxonomy_id = null })
        // Result pagination events
        this.local_event_bus.$on("PAGE_CHANGED", page => this.goToPage(page))
    },
    methods: {
        areSearchParameterTheSameAsBefore(current_search_request_body){
            var body_copy = {...current_search_request_body}
            delete body_copy.limit
            delete body_copy.offset
            body_copy = JSON.stringify(body_copy)
            if(body_copy !== this.last_search_parameter){
                this.last_search_parameter = body_copy
                return false
            }
            return true
        },
        search(){
            this.is_searching = true
            var request_body = {...this.search_request_body}
            // Reset the results and request the count if the search parameters differ from the one before and no errors occured during the last search, then reset the results and request the count
            var is_same_search = this.areSearchParameterTheSameAsBefore(request_body)
            if(!is_same_search){
                this.results.peptides = null
                this.results.total_count = 0
                this.current_peptide_page = 0
                request_body['include_count'] = true
                request_body.offset = 0
            }
            // Reset errors
            this.errors = {}
            fetch(`${this.$config.macpepdb_backend_base_url}/api/peptides/search`, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request_body)
            }).then(response => {
                if(response.ok) {
                    response.json().then(response_data => {
                        if(!is_same_search) this.results.total_count = response_data.count
                        this.results.peptides = response_data.peptides
                        this.$el.querySelector('.peptides').scrollIntoView(true)
                    })
                } else if(response.status == 422) {
                    response.json().then(response_data => {
                        this.errors = response_data.errors
                        this.errors.lower_tolerance = this.errors.lower_precursor_tolerance_ppm
                        this.errors.upper_tolerance = this.errors.upper_precursor_tolerance_ppm
                    })
                } else {
                    this.handleUnknownResponse(response)
                }
            }).finally(() => {
                this.is_searching = false
            })
        },
        getFileNameFromContentDispostionHeader(header, fallback){
                var filename_reg = /filename=(?<filename>[\w\.]+)(;|\b|$)/
                var matches = header.match(filename_reg)
                return matches.groups.filename || fallback
        },
        goToPage(page){
            this.current_result_page = page
            this.search()
        },
        toggleFilterVisibility(){
            this.show_filter_inputs = !this.show_filter_inputs
        }
    },
    computed: {
        peptides_per_page(){
            return PEPTIDES_PER_PAGE
        },
        search_request_body(){
            var data = {
                precursor: this.search_params.mass,
                modifications: this.search_params.modifications,
                lower_precursor_tolerance_ppm: Number.isInteger(this.search_params.mass_tolerance.lower) ? this.search_params.mass_tolerance.lower : 0,
                upper_precursor_tolerance_ppm: Number.isInteger(this.search_params.mass_tolerance.upper) ? this.search_params.mass_tolerance.upper : 0,
                variable_modification_maximum: Number.isInteger(this.search_params.max_variable_modifications) ? this.search_params.max_variable_modifications : 0,
                limit: this.peptides_per_page,
                offset: this.peptides_per_page * (this.current_result_page - 1),    // page is satrts at 1
                order_by: this.search_params.order.by,
                order_direction: this.search_params.order.direction
            }
            if(this.search_params.taxonomy_id) data['taxonomy_id'] = this.search_params.taxonomy_id
            if(this.search_params.is_reviewed != null) data['is_reviewed'] = this.search_params.is_reviewed
            return data
        },
        download_search_params(){
            var request_body = {...this.search_request_body}
            delete request_body.offset
            delete request_body.limit
            return JSON.stringify(request_body)
        }
    },
    watch: {
        parent_mass(new_value){
            // Listen to parent mass for changes. If value changes and new value is larger than zero set it as mass
            if (new_value > 0) {
                this.search_params.mass = new_value
            }
        }
    }
}
</script>