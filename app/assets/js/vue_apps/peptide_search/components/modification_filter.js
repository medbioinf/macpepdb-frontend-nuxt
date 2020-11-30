
const EMPTY_MODIFICATION = {
    amino_acid: null,
    position: null,
    is_static: null,
    delta: null
};

export default {
    delimiters: ['[[',']]'],
    data(){
        return {
            new_modification: {...EMPTY_MODIFICATION},
            show_invalid_new_modification_alert: false
        };
    },
    methods: {
        addModification(){
            if(this.validateNewModification()){
                this.show_invalid_new_modification_alert = false;
                this.$store.commit('addModification', this.new_modification);
                this.new_modification = {...EMPTY_MODIFICATION};
            } else {
                this.show_invalid_new_modification_alert = true;
            }
        },
        removeModification(modification_idx){
            this.$store.commit('removeModification', modification_idx);
        },
        setVariableModificationMaximum(event){
            var value = parseInt(event.target.value);
            if(!Number.isNaN(value) && value > -1 )
                this.$store.commit('setVariableModificationMaximum', value);
            else
                this.$store.commit('setVariableModificationMaximum', 0);
        },
        validateNewModification(){
            return this.new_modification.amino_acid != null
                && this.new_modification.position != null
                && this.new_modification.is_static != null
                && this.new_modification.delta != null
                && Number.parseFloat(this.new_modification.delta) != NaN;
        }
    },
    computed: {
        modifications(){
            return this.$store.state.modification_filter.modifications;
        },
        variable_modification_maximum(){
            return this.$store.state.modification_filter.variable_modification_maximum;
        }
    },
    template: '#modification-filter-template'
};