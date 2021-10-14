<template>
    <div>
        <div class="flex justify-content-center w-100">
            <div class="input-group mb-3">
                <input v-model="sequence" v-on:keyup.enter="search" class="form-control" type="text" placeholder="Sequence">

                <button @click="search" class="btn btn-primary" type="button" >
                    <i class="fas fa-search"></i>
                    search
                </button>
            </div>
        </div>
    </div>
</template>


<script>
import Vue from 'vue'

export default {
    data(){
        return {
            // Inputs
            sequence: null,
        }
    },
    methods: {
        search(event){
            if(event) event.preventDefault()
            this.$router.push({ name: "peptides-sequence", params: { sequence: this.sequence } })
        },
    }
}
</script>