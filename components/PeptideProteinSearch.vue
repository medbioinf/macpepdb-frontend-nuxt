<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model="accession_input" v-on:keyup.enter="setAccession" class="form-control" type="text" placeholder="Accession">

                <button @click="setAccession" class="btn btn-primary" type="button" >
                    <i class="fas fa-search"></i>
                    search
                </button>
            </div>
        </div>
        <FilterableProteinPeptidesList v-if="accession != null" :protein_accession="accession" :selectable="true" :select_button_text="select_button_text" :parent_event_bus="local_event_bus"></FilterableProteinPeptidesList>
    </div>
</template>


<script>
import Vue from 'vue'

const SELECT_BUTTON_TEXT = `use for theoretical mass search <i class="fas fa-arrow-right"></i>`

export default {
    props: {
        // Communication bus with parent
        parent_event_bus: {
            type: Vue,
            required: true
        },
    },
    data(){
        return {
            accession: null,
            accession_input: null,
            local_event_bus: new Vue()
        }
    },
    created(){
        // Listen to peptide selects on local even bus
        this.local_event_bus.$on("PEPTIDE_SELECTED", peptide => {this.setMassFromPeptide(peptide)})
    },
    methods: {
        setAccession(){
            this.accession = this.accession_input
        },
        setMassFromPeptide(peptide){
            // Pass mass of peptide to parent
            this.parent_event_bus.$emit("MASS_SELECTED", peptide.mass)
        }
    },
    computed: {
        select_button_text(){
            return SELECT_BUTTON_TEXT
        }
    }
}
</script>