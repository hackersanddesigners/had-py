/* navigation using waypoints.js */

(function (window, document, undefined) {

'use strict';

  var waypoint = new Waypoint({
    element: document.querySelector('.nav'),
    offset: '-12%',
    handler: function(direction) {
      if (direction == 'down') {
        console.log('cheers 🐟')
        this.element.classList.add('p-fx', 'p-tl', 'pd-a--2', 'z-2', 'bg-white')
      } else {
        console.log('🍄')
        this.element.classList.remove('p-fx', 'p-tl', 'pd-a--2', 'z-2', 'bg-white')
      }
    },
  })

})(window, document);
