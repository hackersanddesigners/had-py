(function (window, document, undefined) {

'use strict';

var nav_wrapper = document.createElement('div');
var nav = document.querySelector('.nav');
var nav_parent = nav.parentNode;
var mm_wrapper = document.createElement('div');
var main_menu = document.querySelector('.main-menu');
var mm_parent = main_menu.parentNode;
var sm = document.querySelector('.section-menu');
var toggle = document.createElement('button');

function on_resizing (event) {

  var ww = window.innerWidth;

  sticky();

  // unwrap sb if > 640 and !sticky
  if (ww > 640 && !nav.classList.contains('sticky')) {

    if (document.body.contains(toggle)) {
      unwrap_sb();
    }

  } else {
    if (!document.body.contains(mm_wrapper)) {
      wrap_sb();
    }

  }
  
}

function wrap_sb () {
  // hide `sm`
  sm.classList.add('d-n');

  // set `nav_wrapper` as `nav`'s parent
  nav_parent.replaceChild(nav_wrapper, nav);
  nav_wrapper.appendChild(nav);

  mm_parent.replaceChild(mm_wrapper, main_menu);
  mm_wrapper.appendChild(main_menu);
  mm_wrapper.classList.add('mm_wrapper', 'flex-r', 'flex-sb', 'flex-ab');
  
  nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'z-2');

  nav_wrapper.nextElementSibling.classList.remove('mg-t--3');
  var nav_wh = nav_wrapper.offsetHeight;
  nav_wrapper.nextElementSibling.style.paddingTop = nav_wh + 'px';

  nav.classList.add('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  nav.classList.remove('mg-b--2');
  
  // set up `toggle`
  toggle.classList.add('z-3', 'p-abs', 'p-tr', 'pd-t--1','pd-r--1', 'ft-2', 'ft-3__m', 'blue');
  toggle.innerHTML = '•••';
  nav_wrapper.insertBefore(toggle, nav);
}

function unwrap_sb() {
  nav_wrapper.removeChild(toggle);
  unwrap(nav_wrapper);
  unwrap(mm_wrapper);

  nav.classList.remove('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  sm.classList.remove('d-n');
}

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
    // wrap/unwrap sb if ww > 640
    if (y > threshold) {
      nav.classList.add('sticky');
      
      if (window.innerWidth > 640 && !document.body.contains(mm_wrapper)) {
        wrap_sb();
      }
    } else {
      nav.classList.remove('sticky');

      if (window.innerWidth > 640 && document.body.contains(toggle)) {
        unwrap_sb();
      }
    }

  }
}

function unwrap(wrapper) {
  var doc_frag = document.createDocumentFragment();
  while (wrapper.firstChild) {
    var child = wrapper.removeChild(wrapper.firstChild);
    doc_frag.appendChild(child);
  }
  wrapper.parentNode.replaceChild(doc_frag, wrapper);
}

function sm_toggle (event) {
  if (sm.classList.contains('d-n')) {
    sm.classList.remove('d-n');
    sm.classList.add('pd-b--2', 'pd-b--1__m');
  } else {
    sm.classList.add('d-n');
    sm.classList.remove('pd-b--2', 'pd-b--1__m');
  }
}

// - - - - -

document.addEventListener('DOMContentLoaded', on_resizing, true);
window.addEventListener('resize', on_resizing, true);

toggle.addEventListener('click', sm_toggle, false);

})(window, document);
