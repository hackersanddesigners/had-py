(function (window, document, undefined) {

'use strict';
  
var nav_wrapper = document.createElement('div');
var nav = document.querySelector('.nav');
var nav_parent = nav.parentNode;
var main_menu = document.querySelector('.main-menu');
var section_menu = document.querySelector('.section-menu');
var sm = document.createElement('button');
var sm_i = document.querySelectorAll('.sm-item');
var after_nav = nav.nextElementSibling;

function onResizing (event) {
  
  // --- set scroll trigger
  var threshold = nav.offsetHeight;
  var trigger = threshold / 2;

  window.onscroll = function (event) {
    requestAnimationFrame(checkSticky);
  };
    
  // --- set function to check for scroll trigger
  function checkSticky() {
    var y = window.scrollY - trigger;

    if (y > threshold) {
      if (!nav.classList.contains('sticky')) {

      // hide `nav`
      nav.classList.add('sticky', 'd-n');

      // set `nav_wrapper` as `nav`'s parent
      nav_parent.replaceChild(nav_wrapper, nav);
      nav_wrapper.appendChild(nav);
      nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'z-2');
      nav.classList.remove('mg-b--2');
      
      // set up `sm`
      sm.classList.add('z-3', 'p-abs', 'p-tr', 'pd-r--1', 'ft-2', 'ft-3__m', 'blue');
      sm.innerHTML = '•••';
      nav_wrapper.insertBefore(sm, nav);
    
      after_nav.style.paddingTop = threshold + 'px';
    }
  } else if (nav.classList.contains('sticky')) {
    nav.classList.remove('sticky', 'd-n', 'pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
        
    for(var i = 0; i < sm_i.length; i++) {
      sm_i[i].classList.remove('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
      sm_i[i].classList.add('mg-r--1', 'mg-b--05');
    }

    // unwrap section menu
    nav_wrapper.removeChild(sm);
    unwrap(nav_wrapper);

    section_menu.classList.remove('d-ib', 'flex-r', 'flex-ab', 'flex-sb');

    after_nav.style.paddingTop = '';
   }
  } // --- end of checkSticky()
} // --- end resize()

function unwrap(wrapper) {
  var doc_frag = document.createDocumentFragment();
  while (wrapper.firstChild) {
    var child = wrapper.removeChild(wrapper.firstChild);
    doc_frag.appendChild(child);
  }
  wrapper.parentNode.replaceChild(doc_frag, wrapper);
}

function section_menu_toggle (event) {
  if (nav.classList.contains('d-n')) {
    nav.classList.remove('d-n');
    nav.classList.add('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
    nav_wrapper.classList.add('pd-b--1');
    section_menu.classList.add('flex-r', 'flex-ab', 'flex-sb');
    
    for(var i = 0; i < sm_i.length; i++) {
      sm_i[i].classList.remove('mg-r--1', 'mg-b--05');
      sm_i[i].classList.add('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
    }
  } else {
    nav.classList.add('d-n');
    nav.classList.remove('pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
    nav_wrapper.classList.remove('pd-b--1');
    section_menu.classList.remove('d-ib');
    
    for(var i = 0; i < sm_i.length; i++) {
      sm_i[i].classList.remove('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
    }
  }
}

// - - - - -

window.onresize = onResizing;
window.onload = onResizing;

sm.addEventListener('click', section_menu_toggle, false);

})(window, document);
