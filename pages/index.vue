<template>
  <div class="dashboard">
    <h1>Welcome to MaCPepDB - Mass Centric Peptide Database</h1>
    <div class="card mb-3">
      <div class="card-body">
        <p>From here you have two options to search the database:</p>
        <ol>
          <li>Start by searching for a protein by its Accession. From here you can search the peptides contained in the protein.</li>
          <li>Start by searching for peptides. There are several possibilities. Search directly for a sequence or a weight, digest a sequence or a protein and use the weight of one of the resulting peptides. You also have the possibility to refine the search with various filters.</li>
          <p>Both options are available in the menu.</p>
        </ol>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col">
        <div class="card mb-3">
          <div class="card-header">
            Citation and publication
          </div>
          <div class="card-body">
            <ul>
              <li>
                  <div class="d-flex flex-column">
                    <span class="fw-bold">MaCPepDB: A Database to Quickly Access All Tryptic Peptides of the UniProtKB</span>
                    <span>Julian Uszkoreit, Dirk Winkelhardt, Katalin Barkovits, Maximilian Wulf, Sascha Roocke, Katrin Marcus, and Martin Eisenacher</span>
                    <span>Journal of Proteome Research 2021 20 (4), 2145-2150</span>
                    <a href="https://doi.org/10.1021/acs.jproteome.0c00967" target="_blank" class="font-weight-bold"> 
                      DOI: 10.1021/acs.jproteome.0c00967
                    </a>
                  </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div v-if="is_dashboard_loaded" class="row mb-3">
      <div class="col col-md-6">
        <div class="card mb-3">
          <div class="card-header">
            Database status
          </div>
          <div class="card-body">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Paramter</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>Maintenance mode</th>
                  <td>{{ database_status.maintenance_mode }}</td>
                </tr>
                <tr>
                  <th>Last finished update</th>
                  <td>{{ database_status.last_update | timestampToIsoDate }}</td>
                </tr>
                <tr>
                  <th>comment</th>
                  <td v-if="comment">{{ comment }}</td>
                  <td v-else> n/a </td>
                </tr>
                <tr>
                  <th>Number of databse nodes online</th>
                  <td>{{ database_status.number_of_nodes }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col col-md-6">
        <div class="card">
          <div class="card-header">
            Digestion paramters
          </div>
          <div class="card-body">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Paramter</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>Enzyme</th>
                  <td>{{ digestion_parameters.enzyme_name }}</td>
                </tr>
                <tr>
                  <th>Allowed missed cleavages</th>
                  <td>{{ digestion_parameters.maximum_number_of_missed_cleavages }}</td>
                </tr>
                <tr>
                  <th>Peptide length</th>
                  <td>{{ digestion_parameters.minimum_peptide_length }} - {{ digestion_parameters.maximum_peptide_length }} </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  mounted(){
    if(!this.is_dashboard_loaded){
      Promise.all([
        this.fetch_maintenance(),
        this.fetch_status()
      ]).finally(() => {
        this.is_dashboard_loaded = true
      })
    }
    
  },
  methods: {
    async fetch_maintenance(){
      return fetch(`${this.$config.macpepdb_backend_base_url}/api/dashboard/maintenance`, {"no-cors": true})
      .then(response => {
        return response.json()
        .then(response_body => {
          this.digestion_parameters = response_body.digestion_parameters
          this.comment = response_body.comment
        })
      })
    },
    async fetch_status(){
      return fetch(`${this.$config.macpepdb_backend_base_url}/api/dashboard/status`, {"no-cors": true})
      .then(response => {
        return response.json()
        .then(response_body => {
          this.database_status = response_body
        })
      })
    }
  },
  computed: {
    is_dashboard_loaded: {
      set(data){
        this.$store.commit("dashboard/setIsLoaded")
      },
      get(){
        return this.$store.state.dashboard.is_loaded
      }
    },
    database_status: {
      set(data){
        this.$store.commit("dashboard/setDatabaseStatus", data)
      },
      get(){
        return this.$store.state.dashboard.database_status
      }
    },
    digestion_parameters: {
      set(data){
        this.$store.commit("dashboard/setDigestionParameters", data)
      },
      get(){
        return this.$store.state.dashboard.digestion_parameters
      }
    },
    comment: {
      set(data){
        this.$store.commit("dashboard/setComment", data)
      },
      get(){
        return this.$store.state.dashboard.comment
      }
    }
  }
}
</script>

<style>
</style>
