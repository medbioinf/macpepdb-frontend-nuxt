export default {
    methods: {
        validateAndSetMassTolerance(commit_method, value){
            value = parseInt(value);
            if(!Number.isNaN(value) && value > -1)
                this.$store.commit(commit_method, value);
            else
                this.$store.commit(commit_method, 0);
        }
    },
    computed: {
        lower_tolerance: {
            get(){
                return this.$store.state.mass_tolerance_filter.lower_tolerance;
            },
            set(value){
                this.validateAndSetMassTolerance('setLowerMassTolerance', value);
            }
        },
        upper_tolerance: {
            get(){
                return this.$store.state.mass_tolerance_filter.upper_tolerance;
            },
            set(value){
                this.validateAndSetMassTolerance('setUpperMassTolerance', value);
            }
        }
    },
    template: '#mass-tolerance-filter-template'
}