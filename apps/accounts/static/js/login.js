const cover = document.getElementById("cover-container");

function handleScroll() {
    if (window.innerWidth > 768) {
        cover.style.transform = "";
        return;
    }

    const scrollY = window.scrollY;
    const coverHeight = window.innerHeight;

    const progress = Math.min(
        scrollY / coverHeight,
        1
    );

    cover.style.transform =
        `translateY(${-progress * 100}%)`;
}

window.addEventListener("scroll", handleScroll, {
    passive: true
});

window.addEventListener("resize", handleScroll);

handleScroll();