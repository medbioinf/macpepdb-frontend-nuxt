var debounce = require('lodash.debounce');
import Delimiters from '../../../vue_mixins/delimiters';

export default {
    mixins: [
        Delimiters
    ],
    props: {
        taxonomy_search_api_url: {
            type: String,
            required: true
        },
    },
    data(){
        return {
            query: null,
            search_results: [],
            is_searching: false
        };
    },
    methods: {
        resetData(){
            for (const [key, value] of Object.entries(DEFAULT_DATA)) {
                this[key] = value;
            }
            this.unselect();
        },
        search: debounce(function(){
            this.is_searching = true;
            var query = this.query;
            // Check if query is a number respectively a taxonomy id
            if(query.match(/\d+/)){
                query = parseInt(query);
            } else {
                // First letter to uppercase
                query = query.charAt(0).toUpperCase() + query.slice(1).toLowerCase();
                // Add wildcard
                query += "*";
            }
            return fetch(this.taxonomy_search_api_url, {
                cache: 'no-cache',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query
                })
            }).then(response => {
                if(response.ok)
                    return response.json()
                else
                    throw new ApiError(response)
            }).then(results => {
                this.search_results = results
            })
            .catch(error => {
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
                this.is_searching = false;
            });
        }, 300),
        select(taxonomy){
            this.query = "";
            this.search_results = [];
            this.$store.commit('selectTaxonomy', taxonomy);
        },
        unselect(){
            this.$store.commit('unselectTaxonomy');
        },
    },
    computed: {
        selected_taxonomy(){
            return this.$store.state.taxonomy_filter.selected_taxonomy;
        }
    },
    watch: {
        query(new_value, old_value){
            if(new_value && new_value != old_value)
                this.search();
        }
    },
    template: '#taxonomy-filter-template'
}