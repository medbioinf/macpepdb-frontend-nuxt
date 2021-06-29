<template>
    <div>
        <div v-if="!is_loading_peptides">
            <button @click="toggleFilterVisibility()" class="btn btn-primary btn-sm" type="button">
                filter
                <i :class="{'fa-caret-down': !show_filter_inputs, 'fa-caret-up': show_filter_inputs}" class="fas"></i>
            </button>
            <div :class="{show: show_filter_inputs}" class="collapse">
                <div class="row mb-3">
                    <label for="maximum-number-of-missed-cleavages" class="col-sm-2 col-form-label">Maximum number of missed cleavages</label>
                    <div class="col-sm-10 d-flex align-items-center">
                        <input v-on:keyup.enter="applyFilters" v-model.number="filter_input.max_missed_cleavages" id="maximum-number-of-missed-cleavages" class="form-control mb-3" type="number" min="0">
                    </div>
                </div>

                <div class="row mb-3">
                    <label for="minimum-peptide-length" class="col-sm-2 col-form-label">Minimum peptide length</label>
                    <div class="col-sm-10 d-flex align-items-center">
                        <input v-model.number="filter_input.min_length" v-on:keyup.enter="applyFilters" :max="filter_input.max_length" id="minimum-peptide-length" class="form-control" type="number" min="0">
                    </div>
                </div>

                <div class="row mb-3">
                    <label for="maximum-peptide-length" class="col-sm-2 col-form-label">Maximum peptide length</label>
                    <div class="col-sm-10 d-flex align-items-center">
                        <input v-model.number="filter_input.max_length" v-on:keyup.enter="applyFilters" :min="filter_input.min_length" id="maximum-peptide-length" class="form-control" type="number">
                    </div>
                </div>
                <div class="row mb-3 d-flex justify-content-end">
                    <div class="col-12 col-md-2 offset-col-md-10 d-flex justify-content-end">
                        <button @click="applyFilters()" class="btn btn-primary btn-sm" type="button">
                            apply
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <table v-if="!is_loading_peptides" class="table table-hover">
            <thead>
                <tr>
                    <th>
                        Sequence
                    </th>
                    <th :colspan="selectable ? 2 : 1">
                        Theoretical mass
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="peptide, idx in peptides_of_current_page" :key="peptide.sequence">
                    <th class="text-break">
                        <NuxtLink :to="{name: 'peptides-sequence', params: {sequence: peptide.sequence}}">{{ peptide.sequence }}</NuxtLink>
                    </th>
                    <td>
                        {{ peptide.mass }}
                    </td>
                    <td v-if="selectable" class="d-flex justify-content-end">
                        <button @click="selectPeptide(idx)" v-html="select_button_text" class="btn btn-outline-primary btn-sm"></button>
                    </td>
                </tr>
            </tbody>
        </table>
        <Spinner v-else class="text-center mb-3"></Spinner>

        <Pagination :parent_event_bus="local_event_bus" :total_items="filtered_peptides.length" :items_per_page="peptides_per_page"></Pagination>
    </div>
</template>

<script>
import Vue from 'vue'

const PEPTIDES_PER_PAGE = 10

export default {
    props: {
        protein_accession: {
            type: String,
            required: true
        },
        // Makes peptides selectable
        selectable: {
            type: Boolean,
            required: false,
            default: false
        },
        // Text for the select button
        select_button_text: {
            type: String,
            required: false,
            default: "select"
        },
        // Communication bus with parent
        parent_event_bus: {
            type: Vue,
            required: false,
            default: null
        },
        // Event which is emitted when a peptide is selected
        select_event: {
            type: String,
            required: false,
            default: "PEPTIDE_SELECTED"
        }
    },
    data(){
        return {
            local_event_bus: new Vue(),
            current_peptides_page: 1,
            peptides: [],
            filtered_peptides: [],
            filter_input: {
                min_length: null,
                max_length: null,
                max_missed_cleavages: null 
            },
            show_filter_inputs: false,
            is_loading_peptides: false
        }
    },
    created(){
        this.local_event_bus.$on("PAGE_CHANGED", page => this.goToPage(page))
    },
    mounted(){
        this.loadPeptides()
    },
    methods: {
        async loadPeptides(){
            this.is_loading_peptides = true
            fetch(`${this.$config.macpepdb_backend_base_url}/api/proteins/${this.protein_accession}/peptides`)
            .then(response => {
                if(response.ok){
                    response.json()
                    .then(response_body => {
                        this.peptides = response_body.peptides
                        this.applyFilters()
                    })
                } else {
                    this.handleUnknownResponse(response)
                }
            })
            .finally(() => {
                this.is_loading_peptides = false
            })
        },
        applyFilters(){
            this.filtered_peptides = this.peptides.filter(peptide => {
                return peptide.sequence.length >= this.filter_min_length
                && peptide.sequence.length <= this.filter_max_length
                && peptide.number_of_missed_cleavages <= this.filter_max_missed_cleavages
            });
        },
        toggleFilterVisibility(){
            this.show_filter_inputs = !this.show_filter_inputs
        },
        goToPage(page){
            this.current_peptides_page = page
        },
        selectPeptide(idx){
            // Emit peptide select event to parent if paren event bus is given
            if (this.parent_event_bus){
                this.parent_event_bus.$emit(this.select_event, this.peptides_of_current_page[idx])
            }
        }
    },
    computed: {
        peptides_per_page(){
            return PEPTIDES_PER_PAGE
        },
        peptides_of_current_page(){
            if(this.filtered_peptides.length){
                var start = this.peptides_per_page * (this.current_peptides_page - 1)   // -1 because the pagination is based on 1
                var end = start + this.peptides_per_page
                return this.filtered_peptides.slice(start, end)
            }
            return []
        },
        filter_min_length(){
            return Number.isInteger(this.filter_input.min_length) ? this.filter_input.min_length : Number.NEGATIVE_INFINITY
        },
        filter_max_length(){
            return Number.isInteger(this.filter_input.max_length) ? this.filter_input.max_length : Number.POSITIVE_INFINITY
        },
        filter_max_missed_cleavages(){
            return Number.isInteger(this.filter_input.max_missed_cleavages) ? this.filter_input.max_missed_cleavages : Number.POSITIVE_INFINITY
        }
    },
    watch: {
        protein_accession(){
            this.peptides = []
            this.filtered_peptides = []
            this.loadPeptides()
        }
    }
}
</script>