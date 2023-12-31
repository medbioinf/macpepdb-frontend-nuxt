<template>
    <div>        
        <ul class="nav nav-tabs mb-3">
            <li class="nav-item">
                <button @click="showSearchForSequence(true)" :class="{'active': show_search_for_sequence}" class="nav-link" type="button">
                    Search for sequence
                </button>
            </li>
            <li class="nav-item">
                <button @click="showSearchForTheoreticalMass(true)" :class="{'active': show_search_for_theoretical_mass}" class="nav-link" type="button">
                    Search for theoretical mass
                </button>
            </li>
            <li class="nav-item">
                <button @click="showSearchByProtein(true)" :class="{'active': show_search_by_protein}" class="nav-link" type="button">
                    Search by protein
                </button>
            </li>
        </ul>
        <div class="tab-content">
            <div :class="{'show active': show_search_for_sequence}" class="tab-pane fade">
                <PeptideSequenceSearch></PeptideSequenceSearch>
            </div>
            <div :class="{'show active': show_search_for_theoretical_mass}" class="tab-pane fade">
                <PeptideTheoreticalMassSearch :parent_mass="mass"></PeptideTheoreticalMassSearch>
            </div>
            <div :class="{'show active': show_search_by_protein}" class="tab-pane fade">
                <KeepAlive>
                    <PeptideProteinSearch :parent_event_bus="local_event_bus"></PeptideProteinSearch>
                </KeepAlive>
            </div>
        </div>
    </div>
</template>

<script>
import Vue from 'vue';

export default {
    head(){
        return {
            meta: [
                { hid: 'description', name: 'description', content: "Search peptides by sequence, mass or protein." },
                { hid: 'og-desc', name: 'og:desc', content: "Search peptides by sequence, mass or protein."},
                { hid: 'og-title', property: 'og:title', content: `${this.$config.short_title} - Peptide search` },
            ]
        }
    },
    data(){
        return {
            show_search_for_sequence: true,
            show_search_for_theoretical_mass: false,
            show_search_by_protein: false,
            local_event_bus: new Vue(),
            // Mass which is passed back by PeptideSequenceSearch or PeptideProteinSearch through the event bus
            mass: -1
        }
    },
    created(){
        this.local_event_bus.$on("MASS_SELECTED", mass => this.massSelectedHandle(mass))
    },
    mounted(){
        this.activateTabByUrlQueryParam()
    },
    activated(){
        this.activateTabByUrlQueryParam()
    },
    methods: {
        /**
         * Activates the correct tab from the url query parameter "tab".
         * @function activateTabByUrlQueryParam
         */
        activateTabByUrlQueryParam(){
            if(this.$route.query.tab){
                switch (this.$route.query.tab) {
                    case "search-for-sequence":
                        this.showSearchForSequence()
                        break
                    case "theoretical-mass-search":
                        this.showSearchForTheoreticalMass()
                        break
                    case "search-by-protein":
                        this.showSearchByProtein()
                        break
                }
            }
        },
        showSearchForSequence(is_tab_change = false){
            this.show_search_for_theoretical_mass = false
            this.show_search_by_protein = false
            this.show_search_for_sequence = true
            if(is_tab_change)
                this.$router.replace({name: "peptides-search", query: {tab: "search-for-sequence"}})
        },
        showSearchForTheoreticalMass(is_tab_change = false){
            this.show_search_for_sequence = false
            this.show_search_by_protein = false
            this.show_search_for_theoretical_mass = true
            if(is_tab_change)
                this.$router.replace({name: "peptides-search", query: {tab: "theoretical-mass-search"}})
        },
        showSearchByProtein(is_tab_change = false){
            this.show_search_for_sequence = false
            this.show_search_for_theoretical_mass = false
            this.show_search_by_protein = true
            if(is_tab_change)
                this.$router.replace({name: "peptides-search", query: {tab: "search-by-protein"}})
        },
        massSelectedHandle(mass){
            this.mass = mass
            this.showSearchForTheoreticalMass(true)
        }
    }
}
</script>