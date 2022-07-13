<template>
    <div>
        <h1 id="publications">Publications</h1>
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
        <h1>Posters</h1>
        <ul>
            <li v-for="(url, title) in posters" :key="url">
                <a :href="url">
                    {{ title }}
                    <i class="fas fa-file-download ms-1"></i>
                </a>
            </li>
        </ul>
    </div>
</template>

<script>
import AttributeErrorList from '../components/AttributeErrorList.vue'
export default {
  components: { AttributeErrorList },
    data(){
        return {
            posters: {
                "MaCPepDB: Increasing the performance of the mass centric peptide database with old hardware and a distributed database": 
                    `${this.$config.macpepdb_backend_base_url}/api/documents/20220314-macpepdb__increasing-performance.pdf`,
                "Enhancements of MaCPepDB – the Mass Centric Peptide Database":
                    `${this.$config.macpepdb_backend_base_url}/api/documents/20220331-enhancement_of_macpepdb.pdf`
            }
        }
    }
}
</script>