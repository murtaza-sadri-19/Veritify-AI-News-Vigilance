 // Hide header on scroll down
 let lastScrollTop = 0;
 window.addEventListener("scroll", function() {
     const header = document.querySelector("header");
     const st = window.pageYOffset || document.documentElement.scrollTop;
     if (st > lastScrollTop) {
         header.classList.add("hidden");
     } else {
         header.classList.remove("hidden");
     }
     lastScrollTop = st <= 0 ? 0 : st;
 }, false);