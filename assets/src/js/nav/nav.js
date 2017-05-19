(function (window, document, undefined) {

'use strict';
  
var nav_wrapper = document.createElement('div');
var nav = document.querySelector('.nav');
var nav_parent = nav.parentNode;
var mm_wrapper = document.createElement('div');
var main_menu = document.querySelector('.main-menu');
var mm_parent = main_menu.parentNode;
var section_menu = document.querySelector('.section-menu');
var sm = document.createElement('button');
var sm_i = document.querySelectorAll('.sm-item');
var intro = document.querySelector('.intro');

function onResizing (event) {
  
  // --- make toggle menu
  if (window.innerWidth > 640) {
    
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
        
        if (!nav.classList.contains('sticky') && nav.parentNode !== nav_wrapper) {
          nav.classList.add('sticky');

          // set `nav_wrapper` as `nav`'s parent
          nav_parent.replaceChild(nav_wrapper, nav);
          nav_wrapper.appendChild(nav);

          mm_parent.replaceChild(mm_wrapper, main_menu);
          mm_wrapper.appendChild(main_menu);
          mm_wrapper.classList.add('mm_wrapper', 'flex-r', 'flex-sb', 'flex-ab');
    
          nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'pd-t--1', 'pd-h--2', 'z-2', 'bg-white');
          nav.classList.remove('mg-b--2');
    
          section_menu.classList.add('d-n');
          sm.classList.add('ft-2', 'ft-3_m', 'blue');
          sm.innerHTML = '•••';
          mm_wrapper.appendChild(sm);
        }

      } else if (y < threshold && nav.classList.contains('sticky')) {
        nav.classList.remove('sticky');
        
        for(var i = 0; i < sm_i.length; i++) {
          sm_i[i].classList.remove('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
          sm_i[i].classList.add('mg-r--1', 'mg-b--05');
        }

        // unwrap section menu
        mm_wrapper.removeChild(sm);
        unwrap(nav_wrapper);
        unwrap(mm_wrapper);

        section_menu.classList.remove('d-n', 'd-ib', 'flex-r', 'flex-ab', 'flex-sb');
      }
    } // --- end of checkSticky()

    // unwrap section menu b/t shifting point (640px)
    // this works okay if `y < threshold`, but does not care if `y > threshold` && window is being resized from < 640 to > 640
    // but it works okay if window is being resized from > 640 to < 640 (w/ `threshold > y`)
    if (!nav.classList.contains('sticky') && section_menu.classList.contains('d-n')) {
      // unwrap section menu
      mm_wrapper.removeChild(sm);

      unwrap(nav_wrapper);
      unwrap(mm_wrapper);

      section_menu.classList.remove('d-n', 'd-ib');
    }

  // --- * * *

  } else if (window.innerWidth < 640) {
      if (nav.parentNode !== nav_wrapper) {
        // clean up space between `nav` and `intro p`
        nav.classList.remove('mg-b--2');
    
        // set `nav_wrapper` as `nav`'s parent
        nav_parent.replaceChild(nav_wrapper, nav);
        nav_wrapper.appendChild(nav);

        mm_parent.replaceChild(mm_wrapper, main_menu);
        mm_wrapper.appendChild(main_menu);
        mm_wrapper.classList.add('mm_wrapper', 'flex-r', 'flex-sb', 'flex-ab');

        nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'pd-t--1', 'pd-h--2', 'z-2', 'bg-white');

        // wrap section menu to toggle button
        section_menu.classList.add('d-n');
        sm.classList.add('ft-2', 'ft-3_m', 'blue');
        sm.innerHTML = '•••';
        mm_wrapper.appendChild(sm);
      } else if (nav.classList.contains('sticky')) {
        nav.classList.remove('sticky');
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

function section_menu_toggle (event) {
  if (section_menu.classList.contains('d-n')) {
    section_menu.classList.remove('d-n');
    section_menu.classList.add('flex-r', 'flex-ab', 'flex-sb');
    for(var i = 0; i < sm_i.length; i++) {
      sm_i[i].classList.remove('mg-r--1', 'mg-b--05')
      sm_i[i].classList.add('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
    }
    nav_wrapper.classList.add('pd-b--1');
  } else {
    section_menu.classList.remove('d-ib');
    section_menu.classList.add('d-n');
    for(var i = 0; i < sm_i.length; i++) {
      sm_i[i].classList.remove('w--half', 'w--one-third__m', 'w--one-fourth__l', 'mg-b--1');
    }
    nav_wrapper.classList.remove('pd-b--1');
  }
}

// - - - - -

window.onresize = onResizing;
window.onload = onResizing;

sm.addEventListener('click', section_menu_toggle, false);

})(window, document);
