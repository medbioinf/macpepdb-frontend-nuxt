<template>
    <div id="protein-search">
        <h1>Proteins</h1>
        <div class="flex justify-content-center w-100">
            <form id="protein-accession-search" @submit="search($event)">
                <div class="input-group mb-3">
                    <input class="form-control" type="text" v-model="accession" placeholder="Accession">

                    <button class="btn btn-primary" type="button" @click="search">
                        <i class="fas fa-search"></i>
                        search
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
export default {
    data(){
        return {
            accession: ""
        }
    },
    methods: {
        search(event = null){
            // Prevent default execution
            if(event) event.preventDefault()
            this.$router.push({ name: "proteins-accession", params: { accession: this.accession } })
        }
    }
}
</script>