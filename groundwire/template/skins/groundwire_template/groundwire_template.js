/* Groundwire Template Javascript */

jQuery.fn.firstAndLast = function() {
    this.children('li:first').addClass('first');
    this.children('li:last').addClass('last');
    return this;
}

jQuery(function ($) {
    
   /* Add first and last classes to items in site actions. */ 
   $('#portal-siteactions').firstAndLast();
   $('.documentActions ul').firstAndLast();
   $('#portal-globalnav').firstAndLast();
   
   /* Add a warning about changing the home page display. */
   // Define the message.
   var homeDisplayWarning = 'You are about to change the display of the home page. ';
   homeDisplayWarning += 'This change has the potential to break the site. Do you want to continue?';
   // Identify the home page display links.
   var homeDisplayLinks = $('.section-front-page #plone-contentmenu-display .actionMenuContent a');
   // We have to unbind other click events so that the 'change content item as default view' popup
   // doesn't fire even when the user chooses cancel.
   homeDisplayLinks.unbind('click');
   // Bind our warning to the links' click event.
   homeDisplayLinks.click(function (event) {
      if (!confirm(homeDisplayWarning)) {
          event.preventDefault();
      }
   });
   
   /* Change the default breadcrumb separator. */
   $('#portal-breadcrumbs .breadcrumbSeparator').html('&raquo;');
   
   /* We need to customize the popup configuration for our PFG contact form
      to avoid getting multiple thank you responses. */
   var contact_popup_id = $('#siteaction-contact a').attr('rel');
   $(contact_popup_id).removeData('formtarget')
    .data('selector', '.documentFirstHeading, #fg-base-edit');
   
}); 