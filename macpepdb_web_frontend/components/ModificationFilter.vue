<template>
    <div v-if="modifications">
        <div class="divider">Modifications</div>

        <button @click="toggleHints" class="btn btn-outline-link btn-sm pl-0" type="button">
            Read the modification limitation
            <i :class="{'fa-caret-up': show_hints, 'fa-caret-down': !show_hints}" class="fas"></i>
        </button>

        <div :class="{'show': show_hints}" class="collapse">
            <p>
                Be aware of the following limitations:
            </p>
            <ol>
                <li>A maximum of 9 variable modifications (anywhere and n/c-terminal residue)</li>
                <li>Only 1 static n-terminus modification (applied to the terminus, not the terminal amino acid residue)</li>
                <li>Only 1 static c-terminus modification (applied to the terminus, not the terminal amino acid residue)</li>
                <li>Static modification for the terminal residues are not possible</li>
            </ol>
        </div>

        <div class="row mb-3">
            <label for="variable-modification-maximum" class="col-sm-2 col-form-label">Variable modification maximum*</label>
            <div class="col-sm-10 d-flex align-items-center">
                <input v-model.number="max_variable_modifications" id="variable-modification-maximum" class="form-control mb-3" type="number" min="0">
            </div>
        </div>

        
        <div class="input-group mb-3">
            <select class="form-select" v-model="new_modification.amino_acid">
                <option :value="null" disabled>Amino acid</option>
                <option v-for="amino_acid in amino_acids" :key="amino_acid.one_letter_code" :value="amino_acid.one_letter_code">{{amino_acid.one_letter_code}} - {{amino_acid.name}}</option>
            </select>

            <select class="form-select" v-model="new_modification.position">
                <option :value="null" disabled>Position</option>
                <option v-for="position in modification_positions" :key="position" :value="position">{{position}}</option>
            </select>

            <select class="form-select" v-model="new_modification.is_static">
                <option :value="null" disabled>Type</option>
                <option :value="true">static</option>
                <option :value="false">variable</option>
            </select>

            <input class="form-control" type="number" v-model.number="new_modification.delta" placeholder="Modification mass (in Dalton)" step="any" >

            <button type="button" class="btn btn-primary" @click="addModification()">
                <i class="fas fa-plus"></i>
                Add modification
            </button>
        </div>

        <div v-if="show_invalid_new_modification_alert" class="alert alert-danger mt-3 px-1 py-1" role="alert">
            Please choose an amino acid, a position, a type and a weight to create a new modification.
        </div>

        <table class="table mb-3" v-if="modifications.length">
            <thead>
                <tr>
                    <th>
                        Amino acid
                    </th>
                    <th>
                        Position
                    </th>
                    <th>
                        Type
                    </th>
                    <th colspan="3">
                        Mass delta
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(modification, idx) in modifications" :key="idx">
                    <td>
                        {{ modification.amino_acid }}
                    </td>
                    <td>
                        {{ modification.position }}
                    </td>
                    <td>
                        {{ modification.is_static ? 'static' : 'variable' }}
                    </td>
                    <td>
                        {{ modification.delta }}
                    </td>
                    <td>
                        <small v-if="errors[`modifictions_${idx}`]">
                            <AttributeErrorList :errors="errors[`modifictions_${idx}`]"></AttributeErrorList>
                        </small>
                    </td>
                    <td>
                        <button class="btn btn-danger btn-sm" type="button" @click="removeModification(idx)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
                <tr v-if="!modifications.length">
                    <td colspan="5">
                        No modifications added
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import Vue from 'vue'

const EMPTY_MODIFICATION = {
    amino_acid: null,
    position: null,
    is_static: null,
    delta: null
}

export default {
    props: {
        parent_event_bus: {
            type: Vue,
            required: true
        },
        modifications: {
            type: Array,
            required: true
        },
        errors: {
            type: Object,
            required: false,
            default: {}
        }
    },
    data(){
        return {
            amino_acids: [],
            max_variable_modifications: null,
            modification_positions: [],
            new_modification: {...EMPTY_MODIFICATION},
            show_invalid_new_modification_alert: false,
            show_hints: false
        };
    },
    created(){
        fetch(`${this.$config.macpepdb_backend_base_url}/api/proteins/amino-acids`)
        .then(response => {
            return response.json()
        })
        .then(response_json => {
            this.amino_acids = response_json.amino_acids
        })
        fetch(`${this.$config.macpepdb_backend_base_url}/api/modifications/positions`)
        .then(response => {
            return response.json()
        })
        .then(response_json => {
            this.modification_positions = response_json.modification_positions
        })
    },
    methods: {
        addModification(){
            if(this.validateNewModification()){
                this.show_invalid_new_modification_alert = false
                this.parent_event_bus.$emit('MODIFICATION_ADDED', this.new_modification)
                this.new_modification = {...EMPTY_MODIFICATION}
            } else {
                this.show_invalid_new_modification_alert = true
            }
        },
        removeModification(modification_idx){
            this.parent_event_bus.$emit('MODIFICATION_REMOVED', modification_idx)
        },
        validateNewModification(){
            return this.new_modification.amino_acid != null
                && this.new_modification.position != null
                && this.new_modification.is_static != null
                && this.new_modification.delta != null
                && Number.parseFloat(this.new_modification.delta) != NaN
        },
        toggleHints(){
            this.show_hints = !this.show_hints
        }
    },
    watch: {
        max_variable_modifications(new_value){
            this.parent_event_bus.$emit("MAX_VARIABLE_MODIFICATION_CHANAGED", new_value)
        }
    }
}
</script>