/* navigation using waypoints.js */

(function (window, document, undefined) {

'use strict';

var main_menu = document.querySelector('.main-menu')
var section_menu = document.querySelector('.section-menu')
var sm = document.createElement('button')

var waypoint = new Waypoint({
  element: document.querySelector('.nav'),
  handler: function(direction) {
    if (direction == 'down') {
      console.log('cheers 🐟')
      this.element.classList.add('p-fx', 'p-tl', 'w--full', 'pd-a--2', 'z-2', 'bg-white')
      section_menu.classList.add('d-n')

      sm.classList.add('sm', 'mg-l--1')
      main_menu.appendChild(sm)
    } else {
      console.log('🍄')
      this.element.classList.remove('p-fx', 'p-tl', 'w--full', 'pd-a--2', 'z-2', 'bg-white')
      section_menu.classList.remove('d-n', 'd-ib')

      sm = document.querySelector('.sm')
      main_menu.removeChild(sm)
    }
  },
  offset: function() {
    return -this.element.clientHeight
  }
})

function section_menu_toggle (event) {
  if (section_menu.classList.contains('d-n')) {
    section_menu.classList.remove('d-n')
    section_menu.classList.add('d-ib')
  } else {
    section_menu.classList.remove('d-ib')
    section_menu.classList.add('d-n')
  }
}

sm.addEventListener('click', section_menu_toggle, false)

})(window, document);
