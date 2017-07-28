(function (window, document, undefined) {

'use strict';

var nav = document.querySelector('.nav');
var main_menu = document.querySelector('.main-menu');
var mm_parent = main_menu.parentNode;
var sm = document.querySelector('.section-menu');
var toggle = document.createElement('button');
var main = document.querySelector('main');

function sticky () {
  // --- set scroll trigger
  var threshold = nav.offsetHeight;
  var trigger = threshold / 2;

  window.onscroll = function (event) {
    requestAnimationFrame(checkSticky);
  };
    
  // --- set function to check for scroll trigger
  function checkSticky() {
    var y = window.scrollY - trigger;

    // toggle sticky class &&
    // wrap/unwrap sm if ww > 640
    if (y > threshold) {
      nav.classList.add('sticky');
      
      if (window.innerWidth > 640 && !sm.classList.contains('is-active')) {
        wrap_sm();
      }

    } else {
      nav.classList.remove('sticky');

      if (window.innerWidth > 640 && document.body.contains(toggle)) {
        unwrap_sm();
      }

    }

  }
}

function wrap_sm (nh) {
  // hide `sm`
  sm.classList.add('d-n');

  // smooth in nav transition when scrolling
  var nw_wh = main.previousElementSibling.getBoundingClientRect();
  var nwh = nw_wh.height;

  main.classList.remove('mg-t--3');
  main.style.paddingTop = nwh + 'px';

  // nav.classList.add('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  nav.classList.add('p-fx', 'p-tl', 'flex-r', 'flex-sb', 'w--full', 'z-2', 'pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  nav.classList.remove('mg-b--2');
  
  // set up `toggle`
  toggle.classList.add('ft-2', 'ft-3__m', 'blue', 'a--lss');
  toggle.innerHTML = '•••';
  nav.insertBefore(toggle, sm);
}

function unwrap_sm() {
  nav.removeChild(toggle);
  
  nav.classList.remove('p-fx', 'p-tl', 'w--full', 'z-2', 'pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  sm.classList.remove('d-n');

  main.classList.add('mg-t--3');
  main.removeAttribute('style');
}

function sm_toggle (event) {
  if (sm.classList.contains('d-n')) {
    sm.classList.remove('d-n');
    sm.classList.add('pd-b--2', 'pd-b--1__m', 'is-active');
    toggle.classList.add('trs--lss-o');
  } else {
    sm.classList.add('d-n');
    sm.classList.remove('pd-b--2', 'pd-b--1__m', 'is-active');
    toggle.classList.remove('trs--lss-o');
  }
}

function on_resizing (event) {

  var ww = window.innerWidth;
  var wh = window.innerHeight;
  var dh = document.body.scrollHeight;
  
  var n_wh = main.previousElementSibling.getBoundingClientRect();
  var nh = n_wh.height;

  // check if document height 
  // is bigger than window height
  if (dh > wh) {
    sticky();
  }

  // unwrap sm if > 640 and !sticky
  if (ww > 640 && !nav.classList.contains('sticky')) {
    if (document.body.contains(toggle)) {
      unwrap_sm();
    }

  } else {
    wrap_sm(nh);
  }

}


// - - - - -

document.addEventListener('DOMContentLoaded', on_resizing, true);
window.addEventListener('resize', on_resizing, true);

toggle.addEventListener('click', sm_toggle, false);

})(window, document);
