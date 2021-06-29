export const state = () => ({
    is_loaded: false,
    data: {
        "database_status": {
            "last_update": "1970-01-01 00:00",
            "maintenance_mode": "Off"
        },
        "digestion_paramters": {
            "enzyme_name": "",
            "maximum_number_of_missed_cleavages": 0,
            "maximum_peptide_length": 0,
            "minimum_peptide_length": 0
        },
        "partition_boundaries": [],
        "peptide_count": 0,
        "peptide_partitions_svg": ""
    }
})
  
export const mutations = {
    set(state, data) {
        state.data = data
        state.is_loaded = true
    }
}