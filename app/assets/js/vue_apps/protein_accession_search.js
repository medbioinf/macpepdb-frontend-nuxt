import Vue from "vue";
import ApiError from "./api_error";

Vue.config.devtools = process.env.NODE_ENV != 'production';

const protein_accession_search_settings = {
    el: "#protein-accession-search",
    delimiters: ['[[',']]'],
    data: {
        accession: null,
        peptide_accession_api_url: ""
    },
    mounted(){
        this.peptide_accession_api_url = this.$el.getAttribute("action");
    },
    methods: {
        search(event = null){
            // Prevent default execution
            if(event) event.preventDefault();
            window.location.href = this.peptide_accession_api_url.replace("ACCESSION", this.accession)
        }
    }
}


document.addEventListener("DOMContentLoaded", () => {
    var protein_accession_search = document.getElementById("protein-accession-search");
    var protein_accession_search_app = null;
    if (protein_accession_search)
        protein_accession_search_app = new Vue(protein_accession_search_settings);
});