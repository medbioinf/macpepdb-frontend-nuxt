export default {
    methods: {
        setLowerTolerance(event){
            var value = parseInt(event.target.value);
            if(!Number.isNaN(value) && value > -1)
                this.$store.commit('setLowerMassTolerance', value);
            else
                this.$store.commit('setLowerMassTolerance', 0);
        },
        setUpperTolerance(event){
            var value = parseInt(event.target.value);
            if(!Number.isNaN(value) && value > -1)
                this.$store.commit('setUpperMassTolerance', value);
            else
                this.$store.commit('setUpperMassTolerance', 0);
        }
    },
    computed: {
        lower_tolerance(){
            return this.$store.state.mass_tolerance_filter.lower_tolerance;
        },
        upper_tolerance(){
            return this.$store.state.mass_tolerance_filter.upper_tolerance;
        }
    },
    template: '#mass-tolerance-filter-template'
}