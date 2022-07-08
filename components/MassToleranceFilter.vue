<template>
    <div>
        <div class="divider">Precursor tolerance</div>

        <div class="row mb-3">
            <label for="lower-mass-tolerance" class="col-sm-2 col-form-label">Lower precursor tolerance (ppm)*</label>
            <div class="col-sm-10 d-flex flex-column justify-content-center">
                <input v-model.number="lower_tolerance" :max="upper_tolerance" id="lower-mass-tolerance" class="form-control" type="number" min="0">
                <small v-if="errors.lower_tolerance">
                    <AttributeErrorList :errors="errors.lower_tolerance"></AttributeErrorList>
                </small>    
            </div>
        </div>
        <div class="row mb-3">
            <label for="upper-mass-tolerance" class="col-sm-2 col-form-label">Upper precursor tolerance (ppm)*</label>
            <div class="col-sm-10 d-flex flex-column justify-content-center">
                <input v-model.number="upper_tolerance" :min="lower_tolerance || 0" id="upper-mass-tolerance" class="form-control" type="number">
                <small v-if="errors.upper_tolerance">
                    <AttributeErrorList :errors="errors.upper_tolerance"></AttributeErrorList>
                </small> 
            </div>
        </div>
    </div>
</template>

<script>
import Vue from 'vue'

export default {
    props: {
        parent_event_bus: {
            type: Vue,
            required: true
        },
        inital_lower_tolerance: {
            type: Number,
            required: false
        },
        inital_upper_tolerance: {
            type: Number,
            required: false
        },
        errors: {
            type: Object,
            required: false,
            default: {}
        }
    },
    data(){
        return {
            initialization_finished: false,
            lower_tolerance: null,
            upper_tolerance: null
        }
    },
    created(){
        if(this.initial_lower_tolerance != null) this.lower_tolerance = this.inital_lower_tolerance
        if(this.inital_upper_tolerance != null) this.upper_tolerance = this.inital_upper_tolerance
        this.initialization_finished = true
    },
    watch: {
        lower_tolerance(new_value){
            if(this.initialization_finished)
                this.parent_event_bus.$emit("LOWER_TOLERANCE_CHANGED", this.lower_tolerance)
        },
        upper_tolerance(new_value){
            if(this.initialization_finished)
                this.parent_event_bus.$emit("UPPER_TOLERANCE_CHANGED", this.upper_tolerance)
        }
    }
}
</script>