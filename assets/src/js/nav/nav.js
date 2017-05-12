/* navigation using waypoints.js */

(function (window, document, undefined) {

'use strict'
  
var nav_wrapper = document.createElement('div')
var nav = document.querySelector('.nav')
var mm_wrapper = document.createElement('div')
var main_menu = document.querySelector('.main-menu')
var section_menu = document.querySelector('.section-menu')
var sm = document.createElement('button')

var threshold = nav.offsetHeight
var trigger = threshold / 1.5

window.onscroll = function (event) {
  requestAnimationFrame(checkSticky)
}

function checkSticky() {
  var y = window.scrollY - trigger

  var isSticky = nav.classList.contains('sticky')
  if (y > threshold) {
    if (!isSticky) {
      nav.classList.add('sticky')
      
      // set `nav_wrapper` as `nav`'s parent
      var nav_parent = nav.parentNode
      nav_parent.replaceChild(nav_wrapper, nav)
      nav_wrapper.appendChild(nav)

      var mm_parent = main_menu.parentNode
      mm_parent.replaceChild(mm_wrapper, main_menu)
      mm_wrapper.appendChild(main_menu)
      mm_wrapper.classList.add('mm_wrapper', 'flex-r', 'flex-sb')

      main_menu.classList.remove('flex-r', 'flex-sb', 'flex-st_s')
      
      nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'pd-a--2', 'z-2', 'bg-white')
      nav.classList.remove('mg-b--2')

      section_menu.classList.add('d-n')
      sm.classList.add('sm')
      mm_wrapper.appendChild(sm)
    }
  } else if (isSticky) {
    nav.classList.remove('sticky', 'a-eio')

    sm = document.querySelector('.sm')
    mm_wrapper.removeChild(sm)

    unwrap(nav_wrapper)
    unwrap(mm_wrapper)

    section_menu.classList.remove('d-n', 'd-ib')
  }
}

function unwrap(wrapper) {
  var doc_frag = document.createDocumentFragment()
  while (wrapper.firstChild) {
    var child = wrapper.removeChild(wrapper.firstChild)
    doc_frag.appendChild(child)
  }
      
  wrapper.parentNode.replaceChild(doc_frag, wrapper)
}


function section_menu_toggle (event) {
  if (section_menu.classList.contains('d-n')) {
    section_menu.classList.remove('d-n')
    section_menu.classList.add('d-ib', 'pd-t--1')
  } else {
    section_menu.classList.remove('d-ib', 'pd-t--1')
    section_menu.classList.add('d-n')
  }
}

sm.addEventListener('click', section_menu_toggle, false)

})(window, document);
