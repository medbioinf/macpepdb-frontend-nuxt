<template>
    <ul class="retractable-list" :class="{'is-retracted': is_retracted}">
        <slot></slot>
        <li v-if="number_of_elements > 3" @click="toggle" class="retract-toggle">
            <span v-if="is_retracted">...</span>
            <i v-if="is_retracted" class="fas fa-caret-square-down"></i>
            <i v-else class="fas fa-caret-square-up"></i>
        </li>
    </ul>
</template>

<script>
export default {
    props: {
        passed_number_of_elements: {
            type: Number,
            default: -1
        }
    },
    data(){
        return {
            is_retracted: true,
            number_of_elements: -1
        }
    },
    mounted(){
        this.number_of_elements = this.passed_number_of_elements >= 0 ? this.passed_number_of_elements : this.$el.childElementCount - 1
    },
    methods: {
        toggle(){
            this.is_retracted = !this.is_retracted
        }
    },
    watch: {
        "is_retracted": function(new_value, old_value){
            if (new_value){
                this.$nextTick(() => {
                    this.$el.scrollIntoView()
                })
            }
        }
    }
}
</script>

<style lang="sass">
    .retractable-list
        &.is-retracted
            li
                display: none
            li:nth-child(-n+3)
                display: list-item
        li.retract-toggle
            cursor: pointer
            display: list-item
            list-style-type: none
</style>