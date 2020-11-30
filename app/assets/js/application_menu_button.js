document.addEventListener("DOMContentLoaded", () => {
    Array.from(document.getElementsByClassName('application-menu-button')).forEach(button => {
        button.addEventListener('click', () => {
            Array.from(document.getElementsByClassName('application-nav-column')).forEach(menu =>{
                menu.classList.toggle('extended-menu');
                //menu.classList.toggle('collapsed-menu');
            });
        });
    });
});