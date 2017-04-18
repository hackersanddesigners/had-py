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
var browsersync = require('browser-sync').create();

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
	.pipe(browsersync.reload({stream: true}))
	.pipe(notify({ message: 'CSS task complete' }));
});

// Concatenate & Minify JSn
/* gulp.task('scripts:collection', function() {
	return gulp.src('assets/src/js/collection/*.js')
	.pipe(jshint())
	.pipe(jshint.reporter('default'))
	.pipe(concat('collection.js'))
	.pipe(gulp.dest('assets/dist/js/')) // non-minified js file
	.pipe(rename({
		suffix: '.min'
	}))
	.pipe(uglify())
	.pipe(gulp.dest('assets/dist/js/'))
	.pipe(notify({ message: 'Scripts task complete' }));
});

// Scripts
gulp.task('scripts', ['scripts:collection']);
*/

gulp.task('browser-sync', gulp.series('css', function() {
	browsersync.init({
		server: {
			baseDir: "./"
		},
		proxy: 'http://127.0.0.1:5000'
	});
}));

gulp.task('watch', ('browser-sync', function () {
	gulp.watch('assets/src/css/*.css', gulp.series('css'));
}));

// Default Task
gulp.task('default', gulp.series('clean', 'css', 'watch'));
