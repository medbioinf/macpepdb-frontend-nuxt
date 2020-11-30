import Vue from "vue";
import ApiError from "./api_error";

Vue.config.devtools = process.env.NODE_ENV != 'production';

const protein_accession_search_settings = {
    el: "#protein-accession-search",
    delimiters: ['[[',']]'],
    data: {
        accession: null,
        peptide_accession_api_url: "",
        errors: [],
        searching: false
    },
    mounted(){
        this.peptide_accession_api_url = this.$el.getAttribute("action");
    },
    methods: {
        search(event = null){
            // Prevent default execution
            if(event) event.preventDefault();
            // Stop search execution if search is already running
            if(this.searching) return;
            this.errors = [];
            if(this.accession){
                this.searching = true;
                fetch(this.peptide_accession_api_url.replace("ACCESSION", encodeURIComponent(this.accession)), {
                    cache: 'no-cache',
                }).then(response => {
                    if(response.ok)
                        return response.json()
                    else
                        throw new ApiError(response)
                }).then(response_data => {
                    // Remove the accession so on histoy back (browser back) the input file is empty as well
                    this.accession = null;
                    window.location.href = response_data.url;
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
                    this.searching = false;
                });
            } else {
                this.errors = ["please enter an accession"]
            }
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    var protein_accession_search = document.getElementById("protein-accession-search");
    var protein_accession_search_app = null;
    if (protein_accession_search)
        protein_accession_search_app = new Vue(protein_accession_search_settings);
});