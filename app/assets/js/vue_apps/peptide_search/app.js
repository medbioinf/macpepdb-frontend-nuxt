// import Vue
import Vue from 'vue';
var debounce = require('lodash.debounce');
import ApiError from '../api_error';
import store from './store';
import SequenceDigest from './components/sequence_digest';
import TaxonomyFilter from './components/taxonomy_filter';
import ModificationFilter from './components/modification_filter';
import MassToleranceFilter from './components/mass_tolerance_filter';

// Vue settings
Vue.config.devtools = process.env.NODE_ENV != 'production';

const peptide_search_app_settings = {
    el: "#peptide-search",
    delimiters: ['[[',']]'],
    store,
    components: {
        'sequence_digest': SequenceDigest,
        'taxonomy_filter': TaxonomyFilter,
        'modification_filter': ModificationFilter,
        'mass_tolerance_filter': MassToleranceFilter
    },
    data: {
        // api urls
        peptide_search_api_url: "",
        peptide_api_url: "",
        peptide_url: "",
        //// sequence handling
        sequence_handling: null,
        // render peptide pagination
        peptides_per_page: 0,
        current_peptide_page: 0,
        
        // render parameter
        show_sequence_handling: false,
        show_sequence_digest: false,
        is_getting_sequence_weight: false,
        is_searching_for_peptides: false,

        // results
        peptides: null,
        peptide_count: 0,
        errors: [],

        last_search_parameter: ''
    },
    mounted(){
        this.$el.querySelector("form").addEventListener("submit", event => event.preventDefault());
        this.peptide_search_api_url = this.$el.dataset.peptideSearchApiUrl;
        this.peptide_api_url = this.$el.dataset.peptideApiUrl;
        this.peptide_url = this.$el.dataset.peptideUrl;
        this.taxonomy_search_api_url = this.$el.dataset.taxonomySearchApiUrl;
        this.peptides_per_page = parseInt(this.$el.dataset.peptidesPerPage);
        this.peptide_weight_api_url =  this.$el.dataset.peptideWeightApiUrl;
    },
    methods: {
        resetSearch(){
            this.peptides = null;
            this.peptide_count = 0;
            this.$store.commit('setMass', null);
        },
        setSequence(event){
            this.$store.commit('setSequence', event.target.value);
        },
        setTheoreticalMass(event){
            var value = parseFloat(event.target.value);
            if(!Number.isNaN(value) && value >= 0.0){
                this.$store.commit('setTheoreticalMass', value);
                this.$store.commit('setMass', value);
            } else if (!Number.isNaN(value) && value < 0.0){
                this.$store.commit('setTheoreticalMass', 0.1);
                this.$store.commit('setMass', 0.1);
            } else {
                this.$store.commit('setTheoreticalMass', null);
                this.$store.commit('setMass', null);
            }

        },
        setProteinAccession(event){
            this.$store.commit('setProteinAccession', event.target.value);
        },
        buildSearchData(){
            var data = {
                modifications: this.$store.state.modification_filter.modifications,
                lower_precursor_tolerance_ppm: this.$store.state.mass_tolerance_filter.lower_tolerance,
                upper_precursor_tolerance_ppm: this.$store.state.mass_tolerance_filter.upper_tolerance,
                variable_modification_maximum: this.$store.state.modification_filter.variable_modification_maximum,
                limit: this.peptides_per_page,
                offset: this.current_peptide_page * this.peptides_per_page,
                order_by: this.$store.state.order_by,
                order_direction: this.$store.state.order_direction
            };
            if(this.$store.state.taxonomy_filter.selected_taxonomy) data['taxonomy_id'] = this.$store.state.taxonomy_filter.selected_taxonomy.id;
            if(this.$store.state.is_reviewed != null) data['is_reviewed'] = this.$store.state.is_reviewed;
            data['precursor'] = this.$store.state.mass;
            return data;
        },
        searchPeptidesByWeight(){
            this.is_searching_for_peptides = true;
            this.errors = [];
            var request_body = this.buildSearchData();
            // If the search parameters differ from the on before reset the results and request the count
            var is_same_search = this.areSearchParameterTheSameAsBefore(request_body);
            if(!is_same_search){
                this.peptides = null;
                this.peptide_count = 0;
                this.current_peptide_page = 0;
                request_body['include_count'] = true;
                request_body.offset = 0;
            }
            fetch(this.peptide_search_api_url, {
                method: 'POST',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request_body)
            }).then(response => {
                if(response.ok)
                    return response.json()
                else
                    throw new ApiError(response)
            }).then(response_data => {
                if(!is_same_search) this.peptide_count = response_data.count;
                this.peptides = response_data.peptides;
                this.$el.querySelector('.peptide-matches').scrollIntoView(true);
            }).catch(error => {
                if(error instanceof ApiError){
                    if(error.response.status == 422){
                        error.response.json().then(response_data => {
                            this.errors = response_data.errors;
                        });
                    } else {
                        this.errors = [error.response.statusText];
                    }
                } else {
                    this.errors = ["something unusual has happend, please try again later: " + error];
                }
            }).finally(() => {
                this.is_searching_for_peptides = false;
            });
        },
        getPeptideUrl(peptide){
            return this.peptide_url.replace("SEQUENCE", peptide.sequence);
        },
        goToPeptidePageNumber(page){
            this.current_peptide_page = page;
            this.searchPeptidesByWeight();
        },
        sequenceLookup: debounce(function(){
            this.errors = [];
            fetch(this.peptide_api_url.replace("PEPTIDE", this.sequence), {
                cache: 'no-cache',
            }).then(response => {
                if(response.ok)
                    return response.json()
                else
                    throw new ApiError(response)
            }).then(response_data => {
                this.peptide_count = 1;
                this.peptides = [response_data.peptide];
            }).catch(error => {
                if(error instanceof ApiError){
                    if(error.response.status == 422){
                        error.response.json().then(response_data => {
                            this.errors = response_data.errors;
                        });
                    } else {
                        this.errors = [error.response.statusText];
                    }
                } else {
                    this.errors = ["something unusual has happend, please try again later"];
                }
            });
        }, 250),
        handleSequence(){
            switch(this.sequence_handling){
                case 'sequence_search':
                    this.sequenceLookup();
                    break;
                case 'use_theoretical_mass':
                    this.getSequenceWeight();
                    break;
                case 'digest':
                    this.show_sequence_digest = true;
                    break;
                case null:
                    this.show_sequence_digest = false;
                    break;
            }
        },
        getSequenceWeight: debounce(function(){
            this.is_getting_sequence_weight = true;
            fetch(this.peptide_weight_api_url.replace('SEQUENCE', this.sequence), {
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if(response.ok)
                    return response.json()
                else
                    throw new ApiError(response)
            }).then(response_data => {
                this.$store.commit('setMass', response_data.weight);
            }).catch(error => {
                if(error instanceof ApiError){
                    if(error.response.status == 422){
                        error.response.json().then(response_data => {
                            this.errors = response_data.errors;
                        });
                    } else {
                        this.errors = [error.response.statusText];
                    }
                } else {
                    this.errors = ["something unusual has happend, please try again later"];
                }
            }).finally(() => {
                this.is_getting_sequence_weight = false;
            });
        }, 250),
        areSearchParameterTheSameAsBefore(current_search_request_body){
            var body_copy = {...current_search_request_body};
            delete body_copy.limit;
            delete body_copy.offset;
            body_copy = JSON.stringify(body_copy)
            if(body_copy !== this.last_search_parameter){
                this.last_search_parameter = body_copy;
                return false;
            }
            return true;
        },
        setNewPageManually: debounce(function(event){
            // page index starts with 0, manuall input will be basaed on 1
            var new_page = event.target.value - 1;
            if(new_page < 0) new_page = 0;
            if(new_page > this.peptide_page_count - 1) new_page = this.peptide_page_count - 1;
            this.goToPeptidePageNumber(new_page);
        }, 400),
        setOrderBy(event){
            this.$store.commit('setOrderBy', event.target.value);
        },
        setOrderDirection(event){
            this.$store.commit('setOrderDirection', event.target.value);
        }
    },
    computed: {
        sequence(){
            return this.$store.state.sequence;
        },
        theoretical_mass(){
            return this.$store.state.theoretical_mass;
        },
        protein_accession(){
            return this.$store.state.protein_accession;
        },
        is_mass_valid(){
            return !Number.isNaN(parseFloat(this.$store.state.mass));
        },
        peptide_page_count(){
            return  Math.max(Math.ceil(this.peptide_count/this.peptides_per_page), 1);
            
        },
        peptide_pagination(){
            var pagination = [];
            for(var i = this.current_peptide_page - 2; i <= this.current_peptide_page + 2; i++) pagination.push(i);
            pagination = pagination.filter(page => 0 <= page && page < this.peptide_page_count);
            if(pagination.length > 0){
                if(pagination[0] > 0) pagination.unshift(0, null);
                if(pagination[pagination.length - 1] < this.peptide_page_count - 1) pagination.push(null, this.peptide_page_count - 1);
            }
            return pagination;
        },
        order_by(){
            return this.$store.state.order_by;
        },
        order_direction(){
            return this.$store.state.order_direction;
        },
        is_reviewed: {
            get(){
                return this.$store.state.is_reviewed;
            },
            set(value){
                this.$store.commit('setIsReviewed', value);
            }
        }
    },
    watch: {
        // begin inputs
        theoretical_mass(new_value, old_value){
            if(new_value){
                if(!old_value){
                    // reset other input values
                    this.$store.commit('setProteinAccession', null);
                    this.$store.commit('setSequence', null);
                }
            } else {
                this.resetSearch();
            }
        },
        sequence(new_value, old_value){
            if(new_value){
                if(!old_value){
                    // reset other input values
                    this.$store.commit('setTheoreticalMass', null);
                    this.$store.commit('setProteinAccession', null);
                    // show following filters
                    this.show_sequence_handling = true;
                }
                if(new_value != old_value) {
                    this.handleSequence();
                }
            } else {
                // reset sequence handling
                this.show_sequence_handling = false;
                this.sequence_handling = null;
            }
        },
        protein_accession(new_value, old_value){
            if(new_value){
                if(!old_value){
                    // reset other input values
                    this.$store.commit('setTheoreticalMass', null);
                    this.$store.commit('setSequence', null);
                    // show following filters
                    this.show_sequence_digest = true;
                }
            } else {
                this.show_sequence_digest = false;
                this.resetSearch();
            }
        },
        //// end inputs
        sequence_handling(new_value, old_value){
            if(new_value){
                // if sequence handling was selected before we have to reset some things first
                if (old_value){
                    switch(old_value){
                        case 'sequence_search':
                            this.peptides = null;
                            this.peptide_count = 0;
                            break;
                        case 'theoretical_mass':
                            this.$store.commit('setMass', null);
                            break;
                        case 'digest':
                            this.show_sequence_digest = false;
                            break;
                    }
                }
                this.handleSequence();
            } else {
                this.resetSearch();
                this.$store.commit('setMass', null);
                this.show_sequence_digest = false;
            }
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    var peptide_search = document.getElementById("peptide-search");
    var peptide_search_app = null;
    if (peptide_search)
        peptide_search_app = new Vue(peptide_search_app_settings);
});