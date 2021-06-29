<template>
    <div>
        <div class="divider">Taxonomy settings</div>

        <div class="row mb-3">
            <label for="taxonomy-query" class="col-sm-2 col-form-label">Taxonomy name or ID (optional)</label>
            <div class="col-sm-10 d-flex align-items-center">
                <input id="taxonomy-query" class="form-control" type="text" v-model="query">
            </div>
        </div>

        <div class="d-flex justify-content-center" v-if="is_searching">
            <div class="spinner-border text-primary" role="status"></div>
        </div>

        <ul v-if="!search_results.length && selected_taxonomy" class="list-group">
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ selected_taxonomy.id }} - {{ selected_taxonomy.name }}
                <button @click="unselect()" class="btn btn-danger btn-sm">
                    <i class="fas fa-times"></i>
                </button>
            </li>
        </ul>

        <div class="list-group">
            <button v-for="taxonomy in search_results" :key="taxonomy.id" @click="select(taxonomy)" class="list-group-item list-group-item-action">
                {{ taxonomy.id }} - {{ taxonomy.name }}
            </button>
        </div>
    </div>
</template>

<script>
import Vue from 'vue'
var debounce = require('lodash.debounce')

export default {
    props: {
        parent_event_bus: {
            type: Vue,
            require: true
        }
    },
    data(){
        return {
            query: null,
            search_results: [],
            is_searching: false,
            selected_taxonomy: null
        }
    },
    methods: {
        resetData(){
            for (const [key, value] of Object.entries(DEFAULT_DATA)) {
                this[key] = value
            }
            this.unselect()
        },
        search: debounce(function(){
            this.is_searching = true
            var query = this.query
            // Check if query is a number respectively a taxonomy id
            if(query.match(/\d+/)){
                query = parseInt(query)
            } else {
                // First letter to uppercase
                query = query.charAt(0).toUpperCase() + query.slice(1).toLowerCase()
                // Add wildcard
                query += "*"
            }
            return fetch(`${this.$config.macpepdb_backend_base_url}/api/taxonomies/search`, {
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
                            this.errors = response_data.errors
                        })
                    } else {
                        this.errors = [error.response.statusText]
                    }
                } else {
                    this.errors = ["something unusual has happend, please try again later"]
                }
            })
            .finally(() => {
                this.is_searching = false
            })
        }, 300),
        select(taxonomy){
            this.query = ""
            this.search_results = []
            this.selected_taxonomy = taxonomy
            this.parent_event_bus.$emit("TAXONOMY_SELECTED", taxonomy)
        },
        unselect(){
            this.parent_event_bus.$emit("TAXONOMY_UNSELECTED")
        },
    },
    watch: {
        query(new_value, old_value){
            if(new_value && new_value != old_value)
                this.search()
        }
    }
}
</script>