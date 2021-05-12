var debounce = require('lodash.debounce');

import Delimiters from '../../../vue_mixins/delimiters';
import ApiError from '../../api_error';

export default {
    mixins: [
        Delimiters
    ],
    props: {
        peptides_per_page: {
            type: Number,
            required: true
        },
        digest_api_url: {
            type: String,
            required: true
        },
        show: {
            type: Boolean,
            required: true
        }
    },
    data(){
        return {
            peptides: [],
            page_count: 1,
            current_peptides_page: 0,
            maximum_number_of_missed_cleavages: null,
            minimum_peptide_length: null,
            maximum_peptide_length: null,
            selected_peptide: null,
            errors: [],
            is_digesting: false
        };
    },
    methods: {
        resetData(){
            this.peptides = [];
            this.page_count = 1;
            this.current_peptides_page = 0;
        },
        setSequence(sequence){
            this.protein_accession = null;
            this.sequence = sequence;
        },
        buildDigestData(){
            var data = {
                maximum_number_of_missed_cleavages: this.maximum_number_of_missed_cleavages,
                minimum_peptide_length: this.minimum_peptide_length,
                maximum_peptide_length: this.maximum_peptide_length
            };
            if(this.$store.state.sequence && !this.$store.state.protein_accession)
                data.sequence = this.$store.state.sequence;
            else if (!this.$store.state.sequence && this.$store.state.protein_accession)
                data.accession = this.$store.state.protein_accession;
            return data;
        },
        validateDigestAttributes(){
            this.errors = [];
            if(!Number.isInteger(this.maximum_number_of_missed_cleavages) || !this.maximum_number_of_missed_cleavages < 0)
                this.errors.push("'Maximum number of missed cleavages' is not a number greater or equals than 0.");
            if(!Number.isInteger(this.minimum_peptide_length) || this.minimum_peptide_length < 1)
                this.errors.push("'Minimum peptide length' is not a number greater or equals 1.");
            if(!Number.isInteger(this.maximum_peptide_length) || this.maximum_peptide_length < 1)
                this.errors.push("'Maximum peptide length' is not a number greater or equals 1.");
            if(this.minimum_peptide_length >= this.maximum_peptide_length)
                this.errors.push("'Minimum peptide length' must be greater than 'maximum peptide length'.");
        },
        digestSequenceOrProtein: debounce(function(){
            this.validateDigestAttributes();
            if(this.errors.length == 0 && (this.$store.state.sequence != null || this.$store.state.protein_accession != null)){
                this.is_digesting = true;
                fetch(this.digest_api_url, {
                    method: 'POST',
                    cache: 'no-cache',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.buildDigestData())
                }).then(response => {
                    if(response.ok)
                        return response.json()
                    else
                        throw new ApiError(response)
                }).then(response_data => {
                    this.peptides = response_data.peptides;
                    this.page_count = Math.ceil(this.peptides.length/this.peptides_per_page);
                    this.show_digested_peptides = true;
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
                })
                .finally(() => {
                    this.is_digesting = false;
                });
            } else {
                this.peptides = [];
                this.show_digested_peptides = false;
            }
        }, 300),
        goToPage(page){
            this.current_peptides_page = page;
            this.$el.scrollIntoView(true);
        },
        setSelectedPeptide(peptide){
            if(this.selected_peptide == null || this.selected_peptide.sequence != peptide.sequence){
                this.selected_peptide = peptide;
                this.$store.commit('setMass', peptide.mass);
            } else {
                this.selected_peptide = null;
                this.$store.commit('setMass', null);
            }
        }
    },
    computed: {
        peptides_of_current_page(){
            if(this.peptides){
                var start = this.current_peptides_page * this.peptides_per_page;
                var end = start + this.peptides_per_page;
                return this.peptides.slice(start, end);
            }
            return [];
        }
    },
    watch: {
        maximum_number_of_missed_cleavages(){
            this.digestSequenceOrProtein();
        },
        minimum_peptide_length(){
            this.digestSequenceOrProtein();
        },
        maximum_peptide_length(){
            this.digestSequenceOrProtein();
        },
        show(new_value, old_value){
            // every time this changes from true to false we reset the data property
            if(!new_value && old_value) this.resetData();
        }
    },
    template: '#sequence-digest-template'
}