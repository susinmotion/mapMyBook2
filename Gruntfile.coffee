module.exports = (grunt) ->
  grunt.initConfig
  
    pkg: grunt.file.readJSON("package.json")

    # Run Flask
    shell:
      pythonServer:
        options:
          stdout: true
        command: 'python run.py &'
          
    # SASS -> CSS
    compass:
      options:
        sassDir: "app/sass"
        cssDir: "app/css"
        raw: 'preferred_syntax = :sass\n'
      debugsass: true
    
    # Watch
    watch:
      livereload:
        files: ["app/*"]
        options:
          livereload: true
      style:
        files: ["src/**/*.sass", "src/**/*.css"]
        tasks: ["compass"]
      html:
        files: ["src/**/*.html"]
        tasks: ["htmlmin"]
        
  grunt.loadNpmTasks "grunt-contrib-compass"
  grunt.loadNpmTasks "grunt-contrib-watch"
  grunt.loadNpmTasks "grunt-shell"
  
  grunt.registerTask "build", ["compass", "shell"]
  
  grunt.registerTask "dev", ["build", "watch"]

  grunt.registerTask "default", ["dev"]

