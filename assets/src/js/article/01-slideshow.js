(function (window, document, undefined) {

'use strict'

var gallery = document.querySelector('.gallery')

var slideshow = new Flickity (gallery, {
  adaptiveHeight: false,
  cellAlign: 'center',
  contain: false,
  imagesLoaded: true,
  lazyLoad: true,
  percentPosition: false,
  prevNextButtons: false,
  pageDots: true,
  resize: true,
  wrapAround: true
});

function slideshow_next (event) {
  slideshow.next(true)
}

gallery.addEventListener('click', slideshow_next, false)

})(window, document);
