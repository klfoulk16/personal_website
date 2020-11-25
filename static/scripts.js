
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
