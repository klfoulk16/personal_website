// Dynamic phone menu
function showMenu() {
    // expand phone header menu
    const phone_menu_btn = document.getElementById('phone-menu-btn');
    const phone_menu_elements = document.getElementsByClassName('phone-menu-dropdown');

    if (phone_menu_elements[0].style.display == 'block') {
        for (var i = 0; i < phone_menu_elements.length; i++) { 
        phone_menu_elements[i].style.display = 'none';
        }
        phone_menu_btn.textContent = 'Menu';
    } else {
        for (var i = 0; i < phone_menu_elements.length; i++) { 
            phone_menu_elements[i].style.display = 'block';
        }
        phone_menu_btn.textContent = 'Hide';
    }
};

// Using the modal window
//Get the Modal
var modal = document.getElementById('subscribe_modal');
//Get button that opens modal
var open = document.getElementById('subscribe-link');
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

// Handle Interactive subscribe popup
var subscribe_form = document.getElementById('subscribe-form');
var dup_email_message = document.getElementById('subscribe-dup-email-message');
subscribe_form.addEventListener("submit", subscribe_handler);

async function subscribe_handler(event) {
    /* send subscriber and retrieve json representation */
    const response = await ajaxifyForm(event);

    console.log(response);

    if (response.statusText == "Duplicate Email") {
        dup_email_message.style.display = 'block';
    }
    else if (response.status == 200) {
        var form = document.getElementById('subscribe-form')
        var message = document.getElementById('subscribe-success-message')
        var initial_message = document.getElementById('initial-subscribe-message');
        form.style.display = 'none';
        initial_message.style.display = 'none';
        dup_email_message.style.display = 'none';
        message.style.display = 'block';
    }
}

async function ajaxifyForm(event) {
    /* we don't want the usual behaviors (like reloading the page) */
    event.preventDefault();

    /* get the form, then populate a new FormData from it. */
    var form = event.target;
    var formData = new FormData(form);

    /* get the route that the form sends data to */
    var url = form.action;

    /* submit the request. Careful modifying this - it was the source of many a headache. */
    return await fetch(url, {
    method : 'POST',
    mode: 'cors',
    credentials: 'same-origin',
    cache : "no-cache",
    referrerPolicy: 'no-referrer',
    redirect: 'follow',
    body: formData,
    });
}