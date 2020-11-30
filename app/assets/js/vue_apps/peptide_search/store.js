import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        // search targets
        sequence: null,
        theoretical_mass: null,
        protein_accession: null,
        // parameter for actual search
        mass: null,
        // filter parameters (contains only parameters which are necessary for the search, additional parameters (e.g. for rendering) contained in the filter components themself)
        modification_filter: {
            modifications: [],
            variable_modification_maximum: 0
        },
        taxonomy_filter: {
            selected_taxonomy: null
        },
        mass_tolerance_filter: {
            lower_tolerance: 0,
            upper_tolerance: 0
        }
    },
    mutations: {
        setSequence(state, sequence){
            state.sequence = sequence;
        },
        setTheoreticalMass(state, theoretical_mass){
            state.theoretical_mass = theoretical_mass;
        },
        setProteinAccession(state, protein_accession){
            state.protein_accession = protein_accession;
        },
        setMass(state, mass){
            state.mass = mass;
        },
        setSequence(state, sequence){
            state.sequence = sequence;
        },
        addModification(state, modification){
            state.modification_filter.modifications.push(modification);
        },
        removeModification(state, modification_idx){
            if(0 <= modification_idx && modification_idx < state.modification_filter.modifications.length)
                state.modification_filter.modifications.splice(modification_idx, 1);
        },
        setVariableModificationMaximum(state, variable_modification_maximum){
            state.modification_filter.variable_modification_maximum = variable_modification_maximum;
        },
        selectTaxonomy(state, taxonomy){
            state.taxonomy_filter.selected_taxonomy = taxonomy;
        },
        unselectTaxonomy(state){
            state.taxonomy_filter.selected_taxonomy = null;
        },
        setLowerMassTolerance(state, lower_tolerance){
            state.mass_tolerance_filter.lower_tolerance = lower_tolerance;
        },
        setUpperMassTolerance(state, upper_tolerance){
            state.mass_tolerance_filter.upper_tolerance = upper_tolerance;
        }
    }
});