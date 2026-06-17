const overviewCards = document.querySelectorAll(".overview-card");
const overviewDetail = document.getElementById("overviewDetail");

if (overviewCards.length && overviewDetail) {
    const title = overviewDetail.querySelector("h3");
    const description = overviewDetail.querySelector("p");
    const metrics = overviewDetail.querySelectorAll(".detail-metrics strong");

    overviewCards.forEach((card) => {
        card.addEventListener("click", () => {
            overviewCards.forEach((item) => item.classList.remove("active"));
            card.classList.add("active");

            title.textContent = card.dataset.status;
            description.textContent = card.dataset.description;
            metrics[0].textContent = card.dataset.count;
            metrics[1].textContent = `${card.dataset.percent}%`;
        });
    });
}
