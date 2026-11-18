// Open and close the navigation menu on small screens.
const menuButton = document.getElementById("menuButton");
const navLinks = document.getElementById("navLinks");

if (menuButton && navLinks) {
    menuButton.addEventListener("click", function () {
        navLinks.classList.toggle("show");
    });
}

// Search student cards by name, department or skill.
const studentSearch = document.getElementById("studentSearch");

if (studentSearch) {
    studentSearch.addEventListener("input", function () {
        const searchText = studentSearch.value.toLowerCase();
        const studentCards = document.querySelectorAll(".student-card");

        studentCards.forEach(function (card) {
            const searchableText = card.dataset.search;
            card.style.display = searchableText.includes(searchText) ? "block" : "none";
        });
    });
}
