import Vue from "vue";
import ApiError from "./api_error";
import CodeBlock from "../vue_components/code_block"

Vue.config.devtools = process.env.NODE_ENV != 'production';

const protein_view_settings = {
    el: "#protein-view",
    delimiters: ['[[',']]'],
    components: {
        CodeBlock,
        'codeblock': CodeBlock
    }
}


document.addEventListener("DOMContentLoaded", () => {
    var protein_view = document.getElementById("protein-view");
    var protein_view_app = null;
    if (protein_view)
        protein_view_app = new Vue(protein_view_settings);
});