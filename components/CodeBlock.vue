<template>
    <div class="code-block">
        <div class="code-block-src mb-1 mr-1" :class="[table_type_class]">
            <span class="code-block-src-row" v-for="(line, line_number) in line_separated_code" :key="line_number">
                <span class="text-right pl-2 pr-1 font-monospace border-right border-dark code-block-src-row-number" v-if="line_separated_code.length > 1">{{ line_number }}</span>
                <code class="px-2 text-dark font-monospace">{{ line }}</code>
            </span>
        </div>
        <button type="button" class="btn btn-primary btn-sm" :class="[copy_button_class]" @click="copyCode()">
            <i class="fas fa-copy"></i>
        </button>
    </div>
</template>


<script>
import * as Toastr from 'toastr';

export default {
    props: {
        code: {
            required: true,
            type: String
        },
        identifier: {
            required: true,
            type: String
        },
        line_length: {
            required: false,
            default: 0,
            type: Number
        }
    },
    methods: {
        copyCode(){
            var copy_promise = null;
            // Clipboard API is only accessible within a secure context (https:// or localhost)
            if(navigator.clipboard){
                copy_promise = navigator.clipboard.writeText(this.code);
            } else {
                // The old method is still supported but the Clipboard API is preferred
                var temp = document.createElement('input');
                temp.value = this.code;
                document.body.appendChild(temp);
                temp.select();
                if(document.execCommand("copy"))
                    copy_promise = Promise.resolve();
                temp.remove();
            }

            // If copy promise is still null there is currently no option to get copy to work in this browser
            if(!copy_promise)
                copy_promise = Promise.reject(new Error('Your browser does not support any copy method.'));

            copy_promise.then(() => {
                Toastr.success('copied', '', {timeOut: 1000, positionClass: "toast-bottom-right"}); 
            })
            .catch(error => {
                Toastr.error(error, '', {timeOut: 1000, positionClass: "toast-bottom-right"}); 
            })
        }
    },
    computed: {
        line_separated_code(){
            if(this.line_length > 0){
                var line_separated_code = [];
                for(var i = 0; i < this.code.length; i += this.line_length)
                    line_separated_code.push(this.code.slice(i, i + this.line_length));
                return line_separated_code;
            } else {
                return this.code.split("\n");
            }
        },
        table_type_class(){
            if(this.line_separated_code.length > 1)
                return 'd-table';
            else
                return 'd-inline-table';
        },
        copy_button_class(){
            if(this.line_separated_code.length > 1)
                return 'd-block';
            else
                return 'd-inline-block';
        }
    }
}
</script>