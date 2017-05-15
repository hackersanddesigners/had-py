(function (window, document, undefined) {

  'use strict'

  // Flickity
  var elem = document.querySelector('.gallery');
  var gallery = new Flickity (elem, {
    adaptiveHeight: false,
    cellAlign: 'center',
    contain: false,
    imagesLoaded: true,
    lazyLoad: true,
    percentPosition: false,
    prevNextButtons: true,
    // arrowShape: 'M17.9,39.3c5.3-8.7,5.3-17.3,5.3-17.3s-3.9,8-9.3,15C8.6,43.9,0,49.8,0,49.8s10.7,9.1,13.9,13.3 c3.9,5,6.2,8.2,9.3,14.5c0,0,0-8.6-5.3-17.1C12.6,52,13,52.8,13,52.8l87-0.6v-4.4l-87-0.5C13,47.2,12.6,48,17.9,39.3z',
    pageDots: true,
    resize: true,
    wrapAround: true
  });

})(window, document);
