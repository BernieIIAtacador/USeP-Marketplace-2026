const profileToggle = document.getElementById("profile-toggle");
const profileDropdown = document.getElementById("profile-dropdown");

function closeDropdown() {
    profileDropdown.classList.remove("open");
    profileToggle.setAttribute("aria-expanded", "false");
}

function openDropdown() {
    profileDropdown.classList.add("open");
    profileToggle.setAttribute("aria-expanded", "true");
}

profileToggle.addEventListener("click", (event) => {
    event.stopPropagation();

    if (profileDropdown.classList.contains("open")) {
        closeDropdown();
    } else {
        openDropdown();
    }
});

document.addEventListener("click", (event) => {
    if (!profileDropdown.contains(event.target)) {
        closeDropdown();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeDropdown();
    }
});


// PROFILE PICTURE UPLOAD
// Picking a file submits the form immediately — no separate
// "Save" step for a single-field upload.

const profilePictureInput = document.getElementById("profile-picture-input");
const profilePictureForm = document.getElementById("profile-picture-form");

if (profilePictureInput && profilePictureForm) {
    profilePictureInput.addEventListener("change", () => {
        if (profilePictureInput.files.length > 0) {
            profilePictureForm.submit();
        }
    });
}