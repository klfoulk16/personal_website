
// expand phone header menu

var phone_menu_btn = document.getElementById('phone_menu_btn');

var phone_menu = document.getElementsByClassName('phone_menu');

var lengthOfMenu=phone_menu.length;

phone_menu_btn.addEventListener('click', () => {
    for (var i=0; i<lengthOfMenu; i++) {
        if (phone_menu[i].style.display='none') {
            phone_menu[i].style.display='block'
        } else {
            phone_menu[i].style.display='none'
        };
    };
});
