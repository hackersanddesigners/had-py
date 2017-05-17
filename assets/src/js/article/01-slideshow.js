(function (window, document, undefined) {

  'use strict'

  // Flickity
  var gallery = document.querySelector('.gallery')

  var slideshow = new Flickity (gallery, {
    adaptiveHeight: false,
    cellAlign: 'center',
    contain: false,
    imagesLoaded: true,
    lazyLoad: true,
    percentPosition: false,
    prevNextButtons: true,
    arrowShape: '',
    pageDots: true,
    resize: true,
    wrapAround: true
  });

})(window, document);
