const burger = document.getElementById("burger");
const menu = document.getElementById("menu");

if (burger && menu) {
    burger.onclick = () => {
        menu.classList.toggle("active");
    };
}

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("show");
        }
    });
});

document.querySelectorAll(".hidden").forEach(el => observer.observe(el));

const tourSearch = document.getElementById("tourSearch");
const tourCategory = document.getElementById("tourCategory");
const tourCards = document.getElementById("tourCards");
const modal = document.getElementById("tourModal");
const modalImage = document.getElementById("modalImage");
const modalCategory = document.getElementById("modalCategory");
const modalTitle = document.getElementById("modalTitle");
const modalCountry = document.getElementById("modalCountry");
const modalDescription = document.getElementById("modalDescription");
const modalHighlights = document.getElementById("modalHighlights");
const modalDuration = document.getElementById("modalDuration");
const modalPrice = document.getElementById("modalPrice");
const modalClose = document.querySelector(".modal-close");
const bookingForm = document.getElementById("bookingForm");
const bookingStatus = document.getElementById("bookingStatus");
const bookingNameField = document.getElementById("bookingName");
const bookingEmailField = document.getElementById("bookingEmail");
const bookingDateField = document.getElementById("bookingDate");
const bookingGuestsField = document.getElementById("bookingGuests");
const bookingMessageField = document.getElementById("bookingMessage");
const detailLink = document.getElementById("detailLink");
const bookNowBtn = document.getElementById("bookNowBtn");
const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightboxImage");
const lightboxClose = document.querySelector(".lightbox-close");

let toursData = [];
let currentLightboxIndex = -1;
let galleryImages = [];

async function loadTours() {
    if (tourCards) {
        tourCards.innerHTML = '<div class="empty-state">Завантажуються тури...</div>';
    }

    try {
        const response = await fetch("/api/tours");
        if (!response.ok) {
            throw new Error("Не вдалося завантажити тури");
        }

        toursData = await response.json();
        renderTours();
    } catch (error) {
        if (tourCards) {
            tourCards.innerHTML = '<div class="empty-state">Не вдалося завантажити тури. Спробуйте пізніше.</div>';
        }
    }
}

function renderTours() {
    if (!tourCards) return;

    const searchValue = (tourSearch?.value || "").trim().toLowerCase();
    const selectedCategory = tourCategory?.value || "all";

    const filteredTours = toursData.filter(tour => {
        const matchesSearch =
            tour.name.toLowerCase().includes(searchValue) ||
            tour.country.toLowerCase().includes(searchValue) ||
            tour.summary.toLowerCase().includes(searchValue);

        const matchesCategory =
            selectedCategory === "all" || tour.category === selectedCategory;

        return matchesSearch && matchesCategory;
    });

    if (!filteredTours.length) {
        tourCards.innerHTML = '<div class="empty-state">Нічого не знайдено. Спробуйте інший пошук.</div>';
        return;
    }

    tourCards.innerHTML = filteredTours.map(tour => `
        <article class="card">
            <img src="${tour.image}" alt="${tour.name}" loading="lazy">
            <div class="card-content">
                <p class="card-category">${tour.categoryTitle}</p>
                <h3>${tour.name}</h3>
                <p>${tour.country}</p>
                <p>${tour.summary}</p>
                <div class="card-meta">
                    <span>${tour.duration}</span>
                    <span>${tour.price}</span>
                </div>
                <div class="card-actions">
                    <button class="details-btn" data-tour-id="${tour.id}">Детальніше</button>
                    <a class="view-page-link" href="/tour/${tour.id}" target="_blank" rel="noopener noreferrer">Відкрити сторінку</a>
                </div>
            </div>
        </article>
    `).join("");

    tourCards.querySelectorAll(".details-btn").forEach(button => {
        button.addEventListener("click", () => openTourModal(button.dataset.tourId));
    });
}

tourSearch?.addEventListener("input", renderTours);
tourCategory?.addEventListener("change", renderTours);

function openTourModal(id) {
    const tour = toursData.find(item => item.id === id);
    if (!tour) return;

    modalImage.src = tour.image;
    modalImage.alt = tour.name;
    modalCategory.textContent = tour.categoryTitle;
    modalTitle.textContent = tour.name;
    modalCountry.textContent = tour.country;
    modalDescription.textContent = tour.description;
    modalDuration.textContent = tour.duration;
    modalPrice.textContent = tour.price;

    modalHighlights.innerHTML = tour.highlights
        .map(item => `<li>${item}</li>`)
        .join("");

    detailLink.href = `/tour/${tour.id}`;
    detailLink.target = "_blank";
    detailLink.rel = "noopener noreferrer";
    bookingForm.dataset.tourId = tour.id;
    bookingForm.dataset.tourName = tour.name;
    bookingStatus.textContent = "";
    bookingStatus.className = "form-status";

    modal.classList.remove("hidden");
    document.body.classList.add("modal-open");
}

function closeTourModal() {
    modal.classList.add("hidden");
    document.body.classList.remove("modal-open");
}

bookNowBtn?.addEventListener("click", () => {
    bookingForm.scrollIntoView({ behavior: "smooth", block: "center" });
});

bookingForm?.addEventListener("submit", async event => {
    event.preventDefault();

    const payload = {
        tourId: bookingForm.dataset.tourId || "",
        tourName: bookingForm.dataset.tourName || "",
        name: bookingNameField?.value.trim() || "",
        email: bookingEmailField?.value.trim() || "",
        date: bookingDateField?.value || "",
        guests: bookingGuestsField?.value || "",
        message: bookingMessageField?.value.trim() || ""
    };

    if (!payload.tourId) {
        bookingStatus.textContent = "Спочатку оберіть тур для бронювання.";
        bookingStatus.className = "form-status error";
        return;
    }

    if (!payload.name || !payload.email || !payload.date || !payload.guests) {
        bookingStatus.textContent = "Заповніть всі обов'язкові поля.";
        bookingStatus.className = "form-status error";
        return;
    }

    try {
        const response = await fetch("/api/bookings", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        bookingStatus.textContent = result.message;
        bookingStatus.className = "form-status " + (response.ok ? "success" : "error");

        if (response.ok) {
            bookingForm.reset();
        }
    } catch (error) {
        bookingStatus.textContent = "Не вдалося створити бронювання.";
        bookingStatus.className = "form-status error";
    }
});

modalClose?.addEventListener("click", closeTourModal);

modal?.addEventListener("click", event => {
    if (event.target === modal) {
        closeTourModal();
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeTourModal();
        closeLightbox();
    }

    if (lightbox && !lightbox.classList.contains("hidden")) {
        if (event.key === "ArrowRight") {
            showLightboxImage(1);
        } else if (event.key === "ArrowLeft") {
            showLightboxImage(-1);
        }
    }
});

function openLightbox(src, alt, index = -1) {
    if (!lightbox || !lightboxImage) return;
    lightboxImage.src = src;
    lightboxImage.alt = alt || "Велике фото";
    currentLightboxIndex = index;
    lightbox.classList.remove("hidden");
    document.body.classList.add("modal-open");
}

function closeLightbox() {
    if (!lightbox || !lightboxImage) return;
    lightbox.classList.add("hidden");
    lightboxImage.src = "";
    currentLightboxIndex = -1;
    document.body.classList.remove("modal-open");
}

function showLightboxImage(step) {
    if (!galleryImages.length) return;

    if (currentLightboxIndex < 0) {
        currentLightboxIndex = 0;
    }

    currentLightboxIndex = (currentLightboxIndex + step + galleryImages.length) % galleryImages.length;
    const image = galleryImages[currentLightboxIndex];
    openLightbox(image.src, image.alt, currentLightboxIndex);
}

lightboxClose?.addEventListener("click", closeLightbox);
lightbox?.addEventListener("click", event => {
    if (event.target === lightbox) {
        closeLightbox();
    }
});

document.querySelectorAll(".lightbox-nav-btn").forEach(button => {
    button.addEventListener("click", () => {
        const direction = button.dataset.direction === "next" ? 1 : -1;
        showLightboxImage(direction);
    });
});

function attachGalleryListeners() {
    galleryImages = Array.from(document.querySelectorAll(".grid img"));

    galleryImages.forEach((img, index) => {
        img.addEventListener("click", () => openLightbox(img.src, img.alt, index));
        img.style.cursor = "pointer";
    });
}

attachGalleryListeners();

const reviews = [
    "★★★★★ Відмінний сервіс та вигідні умови.",
    "★★★★★ Подорож була організована на високому рівні.",
    "★★★★★ Обов'язково поїдемо ще раз!"
];

let reviewIndex = 0;
const reviewText = document.getElementById("reviewText");

function nextReview() {
    if (!reviewText) return;
    reviewText.textContent = reviews[reviewIndex];
    reviewIndex = (reviewIndex + 1) % reviews.length;
}

nextReview();
setInterval(nextReview, 3000);

loadTours();