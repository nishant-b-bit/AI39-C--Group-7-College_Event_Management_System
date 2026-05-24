const searchInput = document.getElementById("searchInput");
const genreFilter = document.getElementById("genreFilter");
const eventCards = document.querySelectorAll(".event-card");
 
function filterEvents() {
    const searchValue = searchInput.value.toLowerCase();
    const genreValue = genreFilter.value;
 
    eventCards.forEach(card => {
        const title = card.dataset.title.toLowerCase();
        const genre = card.dataset.genre;
 
        const matchSearch = title.includes(searchValue);
        const matchGenre = genreValue === "all" || genre === genreValue;
 
        if (matchSearch && matchGenre) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}
 
searchInput.addEventListener("input", filterEvents);
genreFilter.addEventListener("change", filterEvents);
 