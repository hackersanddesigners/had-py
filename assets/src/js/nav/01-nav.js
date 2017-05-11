/* navigation using waypoints.js */

(function (window, document, undefined) {

'use strict';
var nav_wrapper = document.createElement('div')
var nav = document.querySelector('.nav')
var main_menu = document.querySelector('.main-menu')
var section_menu = document.querySelector('.section-menu')
var sm = document.createElement('button')

var waypoint = new Waypoint({
  element: document.querySelector('.nav'),
  handler: function(direction) {
    if (direction == 'down') {
      // set `nav_wrapper` as `nav`'s parent
      var parent = nav.parentNode
      parent.replaceChild(nav_wrapper, nav)
      nav_wrapper.appendChild(nav)

      nav_wrapper.classList.add('p-fx', 'p-tl', 'w--full', 'pd-a--2', 'z-2', 'bg-white')
      nav.classList.remove('mg-b--2')

      section_menu.classList.add('d-n')
      sm.classList.add('sm', 'mg-l--1')
      main_menu.appendChild(sm)
    } else {
      // remove `nav_wrapper`
      var doc_frag = document.createDocumentFragment();
      while (nav_wrapper.firstChild) {
        var child = nav_wrapper.removeChild(nav_wrapper.firstChild);
        doc_frag.appendChild(child);
      }
      nav_wrapper.parentNode.replaceChild(doc_frag, nav_wrapper)

      section_menu.classList.remove('d-n', 'd-ib')
      sm = document.querySelector('.sm')
      main_menu.removeChild(sm)
    }
  },
  offset: function() {
    return -nav_wrapper.clientHeight
  }
})

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
