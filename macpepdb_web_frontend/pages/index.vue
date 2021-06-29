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
                  <td>{{ dashboard_data.database_status['maintenance_mode'] }}</td>
                </tr>
                <tr>
                  <th>Last finished update</th>
                  <td>{{ dashboard_data.database_status['last_update'] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
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
                  <td>{{ dashboard_data.digestion_paramters.enzyme_name }}</td>
                </tr>
                <tr>
                  <th>Allowed missed cleavages</th>
                  <td>{{ dashboard_data.digestion_paramters.maximum_number_of_missed_cleavages }}</td>
                </tr>
                <tr>
                  <th>Peptide length</th>
                  <td>{{ dashboard_data.digestion_paramters.minimum_peptide_length }} - {{ dashboard_data.digestion_paramters.maximum_peptide_length }} </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col col-md-6">
        <div class="card">
          <div class="card-header">
            Peptides
          </div>
          <div class="card-body">
            <p><b>Total:</b> {{dashboard_data.peptide_count}}</p>
            <p><b>Peptides per partition</b></p>
            <figure class="matplotlib bar-chart" v-html="dashboard_data.peptide_partitions_svg"></figure>

            <button class="btn btn-outline-link btn-sm pl-0" type="button" data-toggle="collapse" data-target="#peptide-estimation-description" aria-expanded="false" aria-controls="peptide-estimation-description">
              These are only estimates that fluctuate a little from time to time. Read why ....
              <i class="fas"></i>
            </button>

            <div class="collapse" id="peptide-estimation-description">
              <p>
                Counting the peptides with <code>SELECT count(*) ...</code> needs serveral minutes for each partition and locks the table for other operations.
                With PostgreSQLs <code>pg_class</code>-view it is possible to create a good estimation, based on the actual diskspace. This view will change from time to time, due to internal maintenance work by PostgreSQL itself.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-md-12">
        <div class="card">
          <div class="card-header">
            Peptide partition information
          </div>
          <div class="card-body">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Partition</th>
                  <th>Lower boundary (Dalton)</th>
                  <th>Upper boundary (Dalton)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="partition_boundary in dashboard_data.partition_boundaries" :key="partition_boundary[0]">
                  <td>{{ partition_boundary[0] }}</td>
                  <td>{{ partition_boundary[1] }}</td>
                  <td>{{ partition_boundary[2] }}</td>
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
      fetch(`${this.$config.macpepdb_backend_base_url}/api/dashboard`, {"no-cors": true})
      .then(response => {
        response.json()
        .then(response_body => {
          this.dashboard_data = response_body
        })
      })
    }
  },
  computed: {
    is_dashboard_loaded(){
      return this.$store.state.dashboard.is_loaded
    },
    dashboard_data: {
      set(data){
        this.$store.commit("dashboard/set", data)
      },
      get(){
        return this.$store.state.dashboard.data
      }
    }
  }
}
</script>

<style>
</style>
