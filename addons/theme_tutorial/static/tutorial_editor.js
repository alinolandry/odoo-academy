(function() {
	// C'est ici qu'on insert son js, mon alert fonctionne mais le code du tuto ne fonctionne pas
	// alert("je test mon js");
	
    $(document).on("click", ".img-circle", function(){
        alert("Vos préferences ont été enregistré");
    });
/*	
    'use strict';
    var website = odoo.website;
    website.odoo_website = {};
    

    website.snippet.options.snippet_testimonial_options = website.snippet.Option.extend({
        on_focus: function() {
            alert("On focus!");
        }
    })
*/
})();