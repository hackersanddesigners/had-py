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
var main = document.querySelector('main');

function on_resizing (event) {

  var ww = window.innerWidth;
  var wh = window.innerHeight;
  var dh = document.body.scrollHeight
  
  var n_wh = main.previousElementSibling.getBoundingClientRect();
  var nh = n_wh.height;
  console.log('*** nh ' + nh);

  // check if document height 
  // is bigger than window height
  console.log(dh + ' > ' + wh);
  if (dh > wh) {
    sticky();
  }

  // unwrap sm if > 640 and !sticky
  if (ww > 640 && !nav.classList.contains('sticky')) {
    if (document.body.contains(toggle)) {
      unwrap_sm();
    }

  } else {
    if (!document.body.contains(mm_wrapper)) {
      wrap_sm(nh);
    }
  }

}

function wrap_sm (nh) {
  // hide `sm`
  sm.classList.add('d-n');

  // set `nav_wrapper` as `nav`'s parent
  nav_parent.replaceChild(nav_wrapper, nav);
  nav_wrapper.appendChild(nav);

  mm_parent.replaceChild(mm_wrapper, main_menu);
  mm_wrapper.appendChild(main_menu);
  mm_wrapper.classList.add('mm_wrapper', 'flex-r', 'flex-sb', 'flex-ab');
  
  nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'z-2');

  // smooth in nav transition when scrolling
  var nw_wh = main.previousElementSibling.getBoundingClientRect();
  var nwh = nw_wh.height;

  console.log('±± nh ' + nh);

  main.classList.remove('mg-t--3');
  main.style.paddingTop = nwh + 'px';

  nav.classList.add('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  nav.classList.remove('mg-b--2');
  
  // set up `toggle`
  toggle.classList.add('z-3', 'p-abs', 'p-tr', 'pd-t--1','pd-r--1', 'ft-2', 'ft-3__m', 'blue');
  toggle.innerHTML = '•••';
  nav_wrapper.insertBefore(toggle, nav);
}

function unwrap_sm() {
  nav_wrapper.removeChild(toggle);
  unwrap(nav_wrapper);
  unwrap(mm_wrapper);

  nav.classList.remove('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
  sm.classList.remove('d-n');

  main.classList.add('mg-t--3');
  main.removeAttribute('style');
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
    // wrap/unwrap sm if ww > 640
    if (y > threshold) {
      nav.classList.add('sticky');
      
      if (window.innerWidth > 640 && !document.body.contains(mm_wrapper)) {
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
