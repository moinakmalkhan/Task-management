const navItem = document.querySelector(".nav_item");
const menuBtn = document.querySelector(".menu-btn");
const cancelBtn = document.querySelector(".cancel-btn");


menuBtn.onclick = () =>{
    navItem.classList.add("active");
}   
cancelBtn.onclick = () =>{
    navItem.classList.remove("active")
}   


let navLinks = document.querySelectorAll(".nav_item li a");
    for(var i = 0; i < navLinks.length; i++){
        navLinks[i].addEventListener("click", function(){
            navItem.classList.remove("active");
            body.style.overflow = "auto";
        })
    }