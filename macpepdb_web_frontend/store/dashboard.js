export const state = () => ({
    is_loaded: false,
    data: {
        "database_status": {
            "last_update": "1970-01-01 00:00",
            "maintenance_mode": "Off"
        },
        "digestion_parameters": {
            "enzyme_name": "",
            "maximum_number_of_missed_cleavages": 0,
            "maximum_peptide_length": 0,
            "minimum_peptide_length": 0
        },
        comment: null
    },
    is_loaded: false
})
  
export const mutations = {
    set(state, data) {
        state.data = data
        state.is_loaded = true
    }
}