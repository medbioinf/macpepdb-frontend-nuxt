export const state = () => ({
    is_loaded: false,
    database_status: {
        "last_update": 0,
        "maintenance_mode": false,
        "number_of_finished_rebalance_jobs": 0,
        "number_of_nodes": 0,
        "number_of_rebalance_jobs": 0,
        "number_of_running_rebalance_jobs": 0
    },
    digestion_parameters: {
        "enzyme_name": "",
        "maximum_number_of_missed_cleavages": 0,
        "maximum_peptide_length": 0,
        "minimum_peptide_length": 0
    },
    comment: null
})
  
export const mutations = {
    setDatabaseStatus(state, data) {
        state.database_status = data

    },
    setDigestionParameters(state, data) {
        state.digestion_parameters = data
    },
    setComment(state, comment) {
        state.comment = comment
    },
    setIsLoaded(state) {
        state.is_loaded = true
    }
}