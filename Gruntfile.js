// Generated on 2015-01-23 using generator-angular 0.10.0
'use strict';

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {

  // Load grunt tasks automatically
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  // Configurable paths for the application
  var appConfig = {
    dist: '../genweb.cdn/genweb/cdn/dist',
    egg: 'ulearn/theme'
  };

  var config_file = 'ulearn/theme/config.json';
  var resource_config = grunt.file.readJSON(config_file);

  // Define the configuration for all the tasks
  grunt.initConfig({

    // Project settings
    yeoman: appConfig,

    replace: {
      build: {
        src: ['<%= yeoman.egg %>/browser/viewlets_templates/gwcssdevelviewlet.pt'],
        dest: '<%= yeoman.egg %>/browser/viewlets_templates/gwcssproductionviewlet.pt',
        replacements: [{
          from: 'tal:attributes="href string:${portal_url}/++genweb++static',
          to: 'href="../genweb.core/genweb/core/static'
        },
        {
          from: 'tal:attributes="href string:${portal_url}/++components++root',
          to: 'href="../genweb.js/genweb/js/components'
        },
        {
          from: 'tal:attributes="href string:${portal_url}/++components++ulearn',
          to: 'href="../ulearn.js/ulearn/js/components'
        },
        {
          from: 'tal:attributes="href string:${portal_url}/++ulearn++stylesheets',
          to: 'href="ulearn/theme/stylesheets'
        },
        {
          from: 'condition="viewlet/is_devel_mode"',
          to: 'condition="not: viewlet/is_devel_mode"'
        },
        ]
      },
      postbuild: {
        src: ['<%= yeoman.egg %>/browser/viewlets_templates/gwcssproductionviewlet.pt'],
        overwrite: true,
        replacements: [{
          from: 'href="',
          to: 'tal:attributes="href string:${portal_url}/++ulearn++distcss/'
        },
        ]
      }
    },
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
    // Watches files for changes and runs tasks based on the changed files
    watch: {
      gw: {
          files: ['ulearn/theme/scss/*.scss',],
          tasks: ['sass']
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        options: {force: true},
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/ulearn.{,*}*.css',
          ]
        }]
      },
      server: '.tmp'
    },

    cssmin: {
      dist: {
        files: {
          // '<%= yeoman.dist %>/plone.css': resource_config.resources.plone.css.development,
          '<%= yeoman.dist %>/ulearn.css': resource_config.resources.ulearn.css.development
        }
      }
    },

    // Renames files for browser caching purposes
    filerev: {
      dist: {
        src: [
          '<%= yeoman.dist %>/scripts/{,*/}*.js',
          '<%= yeoman.dist %>/styles/{,*/}*.css',
          '<%= yeoman.dist %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}',
          '<%= yeoman.dist %>/styles/fonts/*'
        ]
      },
      build: {
        src: [
          // '<%= yeoman.dist %>/{,*/}*.css',
          '<%= yeoman.dist %>/ulearn.css'
        ]
      }
    },

    // Copies remaining files to places other tasks can use
    copy: {
      build: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'images/{,*/}*.{webp}',
            'fonts/{,*/}*.*'
          ]
        },
        ]
      },
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'images/{,*/}*.{webp}',
            'fonts/{,*/}*.*'
          ]
        }, {
          expand: true,
          cwd: '.tmp/images',
          dest: '<%= yeoman.dist %>/images',
          src: ['generated/*']
        }, {
          expand: true,
          cwd: 'bower_components/bootstrap/dist',
          src: 'fonts/*',
          dest: '<%= yeoman.dist %>'
        }]
      },
      styles: {
        expand: true,
        cwd: '<%= yeoman.app %>/styles',
        dest: '.tmp/styles/',
        src: '{,*/}*.css'
      }
    },
  });

  grunt.registerTask('updateconfig', function () {
    if (!grunt.file.exists(config_file)) {
        grunt.log.error('file ' + config_file + ' not found');
        return true; //return false to abort the execution
    }

    resource_config.revision_info = grunt.filerev.summary; //edit the value of json object, you can also use projec.key if you know what you are updating

    grunt.file.write(config_file, JSON.stringify(resource_config, null, 2)); //serialize it back to file

  });

  grunt.registerTask('default', [
    'watch',
  ]);

  grunt.registerTask('gwbuild', [
    // 'clean:dist',
    'cssmin:dist',
    'filerev:build',
    'updateconfig'
  ]);

};
