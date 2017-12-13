(function (window, document, undefined) {

  'use strict';

  var cover_imgs = document.querySelectorAll('.cover-img');

  for (var i = 0; i < cover_imgs.length; i++) {
    cover_imgs[i].classList.remove('d-n');
    cover_imgs[i].classList.add('lazyload');
  }

})(window, document);
