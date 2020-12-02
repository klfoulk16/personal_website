function showMenu() {
    // expand phone header menu
    const phone_menu_btn = document.getElementById('phone_menu_btn');
    const phone_menu = document.getElementById('phone_menu');

    if (phone_menu.style.display == 'block') {
      phone_menu.style.display = 'none';
      phone_menu_btn.textContent = 'Menu';
    } else {
        phone_menu.style.display = 'block';
        phone_menu_btn.textContent = 'Hide';
    }
};

// Using the modal window
//Get the Modal
var modal = document.getElementById('subscribe_modal');
//Get button that opens modal
var open = document.getElementById('modal_open');
//Get element that closes the modal
var close = document.getElementById('modal_close');
//When user clicks open button, open modal
open.onclick = function() {
    modal.style.display = 'block';
};
// when user clicks on the x, close the modal
close.onclick = function() {
    modal.style.display = 'none';
};
// if user clicks anywhere outside the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

// Display message when someone subscribes.
var subscribe_signup = document.getElementById('subscribe_signup');

subscribe_signup.onclick = function() {
    var form = document.getElementById('subscribe_form')
    var message = document.getElementById('subscribe_message')
    form.style.display = 'none';
    message.style.display = 'block';
};
