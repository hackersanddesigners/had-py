// gulpfile.js

// gulp-packages
var gulp = require('gulp');
var del =  require('del');
var concat = require('gulp-concat');
var rename = require('gulp-rename');

var postcss = require('gulp-postcss');
var cssnext = require('postcss-cssnext');
var nano = require('gulp-cssnano');
var atImport = require('postcss-import');

var jshint = require('gulp-jshint');
var uglify = require('gulp-uglify');
var notify = require("gulp-notify");
var inlinesource = require('gulp-inline-source');

gulp.task('clean', function () {
	return del([
		'assets/dist/**/*']);
});

// Styles
var processors = [
	atImport,
	cssnext({
		'browsers': ['last 2 version'],
		'features': {
			'customProperties': {
				preserve: true,
				appendVariables: true
			},
			'colorFunction': true,
			'customSelectors': true,
			'rem': false
		}
	})
];

gulp.task('css', function(){
	return gulp.src('assets/src/css/style.css')
	.pipe(postcss(processors))
	.pipe(gulp.dest('assets/dist/css'))
	.pipe(nano({discardComments: {removeAll: true}}))
	.pipe(rename({
		suffix: '.min'
	}))
  .pipe(gulp.dest('assets/dist/css'))
});

// Concatenate & Minify JS
gulp.task('scripts:nav', function() {
  return gulp.src('assets/src/js/nav/*.js')
	.pipe(jshint())
  .pipe(jshint.reporter('default'))
  .pipe(concat('nav.js'))
	.pipe(rename({
		suffix: '.min'
	}))
	.pipe(uglify())
	.pipe(gulp.dest('assets/dist/js/'))
});

gulp.task('scripts:article', function() {
 	return gulp.src('assets/src/js/article/*.js')
	.pipe(jshint())
	.pipe(jshint.reporter('default'))
  .pipe(concat('slideshow.js'))
	.pipe(rename({
		suffix: '.min'
	}))
	.pipe(uglify())
	.pipe(gulp.dest('assets/dist/js/'))
});

// Scripts
gulp.task('scripts', gulp.series('scripts:article', 'scripts:nav'));

gulp.task('watch', function() {
  gulp.watch('assets/src/css/*.css', gulp.series('css'));
  gulp.watch('assets/src/js/**/*.js', gulp.series('scripts'));
});

// Default Task
gulp.task('default', gulp.series('clean', 'css', 'scripts', 'watch'));
