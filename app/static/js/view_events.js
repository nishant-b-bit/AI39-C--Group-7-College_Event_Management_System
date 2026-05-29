
const searchInput =
    document.getElementById("searchInput");

const genreFilter =
    document.getElementById("genreFilter");

const cards =
    document.querySelectorAll(".event-card");

function filterEvents() {

    const searchValue =
        searchInput.value.toLowerCase();

    const selectedGenre =
        genreFilter.value.toLowerCase();

    cards.forEach(card => {

        const title =
            card.querySelector("h2")
                .innerText
                .toLowerCase();

        const genre =
            card.dataset.genre.toLowerCase();

        const matchesSearch =
            title.includes(searchValue);

        const matchesGenre =
            selectedGenre === "all" ||
            genre === selectedGenre;

        if (matchesSearch && matchesGenre) {

            card.style.display = "block";

        }
        else {

            card.style.display = "none";

        }

    });

}

searchInput.addEventListener(
    "keyup",
    filterEvents
);

genreFilter.addEventListener(
    "change",
    filterEvents
);
