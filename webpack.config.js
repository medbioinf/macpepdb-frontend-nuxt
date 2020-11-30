const Path = require("path");
const fs = require("fs")
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = (env, argv) => {
    return {
        stats: "minimal",
        mode: "development",
        entry: "./app/assets",
        resolve: {
            alias: {
                'vue$': 'vue/dist/vue.esm.js'
            }
        },
        output: {
            path: Path.resolve(__dirname, "app/static/bundle"),
            filename: "application.js"
        },
        watchOptions: {
            ignored: [
                "app",
                "node_modules",
                "static"
            ]
        },
        module: {
            rules: [
                {
                    test: /\.vue$/,
                    loader: 'vue-loader'
                },
                {
                    test: /\.less$/,
                    use: [
                        {
                            loader: "file-loader",
                            options: {
                                name: "application.css",
                            }
                        },
                        {
                            loader: "extract-loader"
                        },
                        {
                            loader: "css-loader"
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                plugins: function () {
                                    return [
                                        require('autoprefixer')
                                    ];
                                }
                            }
                        },
                        {
                            loader: "less-loader"
                        }
                    ]
                },
                {
                    test: /\.sass$/,
                    use: [
                        {
                            loader: "file-loader",
                            options: {
                                name: "application.css",
                            }
                        },
                        {
                            loader: "extract-loader"
                        },
                        {
                            loader: "css-loader"
                        },
                        {
                            loader: 'postcss-loader',
                            options: {
                                plugins: function () {
                                    return [
                                        require('autoprefixer')
                                    ];
                                }
                            }
                        },
                        {
                            loader: "sass-loader",
                            options: {
                                // sass-loader version >= 8
                                sassOptions: {
                                    indentedSyntax: true,
                                    outputStyle: argv.mode == "production" ? "compressed" : "expanded"
                                }
                            }
                        }
                    ]
                },
                {
                    test: /\.(png|svg|jpg|gif|ico)$/,
                    use: [
                        "file-loader",
                    ],
                },
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/,
                    use: [
                        "file-loader",
                    ],
                }
            ]
        },
        plugins: [
            function() {
                this.hooks.done.tap("WriteBuildTime", function() {env, argv
                    buildtime_file_path = Path.join(__dirname, "app/static/bundle/buildtime.txt");
                    buildtime = Date.now().toString();
                    fs.writeFile(buildtime_file_path, buildtime, function (err) {
                        if (err) return console.log(err);
                        console.log("Buildtime:", buildtime);
                    });
                });
            },
            new VueLoaderPlugin()
        ]
    }
};
