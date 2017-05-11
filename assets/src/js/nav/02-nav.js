/* navigation using waypoints.js */

(function (window, document, undefined) {

'use strict';

  var section_menu = document.querySelector(".section-menu");
  console.log(section_menu);

  var waypoint = new Waypoint({
    element: document.querySelector('.section-menu'),
    handler: function() {
      console.log('cheers 🐟')
    }
  })


})(window, document);
