import Vue from 'vue'

Vue.mixin({
    filters: {
        timestampToIsoDate(timestamp){
            let date = new Date(parseInt(timestamp * 1000));
            return date.toISOString()
        },
    }
})