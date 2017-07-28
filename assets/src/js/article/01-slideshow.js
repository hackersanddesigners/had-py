(function (window, document, undefined) {

'use strict';

var gallery = document.querySelector('.gallery');

if (gallery !== null) {
  var slideshow = new Flickity (gallery, {
    adaptiveHeight: true,
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
    slideshow.next(true);
  }

  gallery.addEventListener('click', slideshow_next, false);
}

})(window, document);
