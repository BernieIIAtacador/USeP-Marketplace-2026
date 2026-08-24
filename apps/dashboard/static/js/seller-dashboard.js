const PRODUCT_CONDITIONS = ['Like new', 'Barely used', 'Good condition', 'For parts'];
const SERVICE_CONDITIONS = ['Available by appointment', 'On-site service', 'Currently unavailable'];

function openModal(modal) {
    if (modal) modal.hidden = false;
}
function closeModal(modal) {
    if (modal) modal.hidden = true;
}

// Generic close buttons (the × and any "Cancel" button with data-close-modal)
document.querySelectorAll('[data-close-modal]').forEach((button) => {
    button.addEventListener('click', () => {
        closeModal(document.querySelector(`#${button.dataset.closeModal}`));
    });
});

// ---- Add listing modal ----
const addListingModal = document.querySelector('#add-listing-modal');
const openAddListing = document.querySelector('#open-add-listing');
if (openAddListing) {
    openAddListing.addEventListener('click', () => openModal(addListingModal));
}

const listingImageInput = document.querySelector('#listing-image');
const listingImagePreview = document.querySelector('#add-listing-modal .image-preview');
const listingUploadBox = document.querySelector('#add-listing-modal .upload-box');
if (listingImageInput && listingImagePreview && listingUploadBox) {
    listingImageInput.addEventListener('change', () => {
        const [file] = listingImageInput.files;
        if (file) {
            listingImagePreview.src = URL.createObjectURL(file);
            listingImagePreview.hidden = false;
            listingUploadBox.hidden = true;
        }
    });
}

const listingCategory = document.querySelector('#listing-category');
const listingCondition = document.querySelector('#listing-condition');
if (listingCategory && listingCondition) {
    listingCategory.addEventListener('change', () => {
        const conditions = listingCategory.value === 'Services' ? SERVICE_CONDITIONS : PRODUCT_CONDITIONS;
        listingCondition.replaceChildren(...conditions.map((c) => new Option(c, c)));
    });
}

// ---- Manage item modal ----
const manageModal = document.querySelector('#manage-item-modal');
const manageStatusBadge = document.querySelector('#manage-status-badge');
const manageImage = document.querySelector('#manage-image');
const manageViews = document.querySelector('#manage-views');
const manageName = document.querySelector('#manage-name');
const manageCategory = document.querySelector('#manage-category');
const managePrice = document.querySelector('#manage-price');
const manageCondition = document.querySelector('#manage-condition');
const manageDescription = document.querySelector('#manage-description');
const manageStatus = document.querySelector('#manage-status');

let activeListingCard = null;

document.querySelectorAll('.manage-button').forEach((button) => {
    button.addEventListener('click', () => {
        const card = button.closest('.seller-listing');
        if (!card) return;
        activeListingCard = card;

        manageImage.src = card.dataset.image;
        manageImage.alt = card.dataset.name;
        manageViews.textContent = card.dataset.views;
        manageName.value = card.dataset.name;
        manageCategory.value = card.dataset.category;
        managePrice.value = card.dataset.price;
        manageDescription.value = card.dataset.description;
        manageStatus.value = card.dataset.statusValue;

        const conditions = card.dataset.category === 'Services' ? SERVICE_CONDITIONS : PRODUCT_CONDITIONS;
        manageCondition.replaceChildren(...conditions.map((c) => new Option(c, c)));
        manageCondition.value = card.dataset.condition;

        const statusClass = card.dataset.statusValue.toLowerCase();
        manageStatusBadge.className = `status-pill status-pill-${statusClass}`;
        manageStatusBadge.textContent = card.dataset.statusValue;

        openModal(manageModal);
    });
});

// Recolor the status select as soon as it changes, just for feedback
if (manageStatus) {
    manageStatus.addEventListener('change', () => {
        const statusClass = manageStatus.value.toLowerCase();
        manageStatus.className = `status-select status-select-${statusClass}`;
    });
}

const manageItemImageInput = document.querySelector('#manage-item-image');
if (manageItemImageInput && manageImage) {
    manageItemImageInput.addEventListener('change', () => {
        const [file] = manageItemImageInput.files;
        if (file) manageImage.src = URL.createObjectURL(file);
    });
}

// ---- Delete confirmation ----
const deleteConfirmModal = document.querySelector('#delete-confirm-modal');
const deleteListingButton = document.querySelector('#delete-listing');
const cancelDeleteButton = document.querySelector('#cancel-delete');
const confirmDeleteButton = document.querySelector('#confirm-delete');

if (deleteListingButton) {
    deleteListingButton.addEventListener('click', () => openModal(deleteConfirmModal));
}
if (cancelDeleteButton) {
    cancelDeleteButton.addEventListener('click', () => closeModal(deleteConfirmModal));
}
if (confirmDeleteButton) {
    confirmDeleteButton.addEventListener('click', () => {
        if (activeListingCard) activeListingCard.remove();
        closeModal(deleteConfirmModal);
        closeModal(manageModal);
    });
}

// ---- Search + status filter (client-side, purely for the demo listings) ----
const listingSearch = document.querySelector('#listing-search');
const listingStatusFilter = document.querySelector('#listing-status-filter');
const listingCards = () => [...document.querySelectorAll('.seller-listing')];
const noResults = document.querySelector('.no-filter-results');

function applyFilters() {
    const status = listingStatusFilter ? listingStatusFilter.value : 'all';
    const search = listingSearch ? listingSearch.value.trim().toLowerCase() : '';
    let visibleCount = 0;

    listingCards().forEach((card) => {
        const matchesStatus = status === 'all' || card.dataset.status === status;
        const matchesSearch = !search || card.dataset.search.includes(search);
        const isVisible = matchesStatus && matchesSearch;
        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
    });

    if (noResults) noResults.hidden = visibleCount > 0;
}

if (listingSearch) listingSearch.addEventListener('input', applyFilters);
if (listingStatusFilter) listingStatusFilter.addEventListener('change', applyFilters);

const listingFiltersForm = document.querySelector('#listing-filters');
if (listingFiltersForm) listingFiltersForm.addEventListener('submit', (e) => e.preventDefault());
