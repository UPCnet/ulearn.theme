module.exports = function (grunt) {
    'use strict';
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                options: {
                    compass: true,
                    // style: 'compressed'
                },
                files: {
                    'ulearn/theme/stylesheets/ulearn.css': 'ulearn/theme/scss/ulearn.scss'
                }
            }
        },
        watch: {
            scripts: {
                files: ['ulearn/theme/scss/*.scss',],
                tasks: ['sass']
            }
        }
    });

    // grunt.loadTasks('tasks');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.registerTask('default', ['watch']);
};
