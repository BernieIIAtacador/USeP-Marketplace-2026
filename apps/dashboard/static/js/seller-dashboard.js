const PRODUCT_CONDITIONS = ['Like new', 'Barely used', 'Good condition', 'For parts'];
const SERVICE_CONDITIONS = ['Available by appointment', 'On-site service', 'Currently unavailable'];

function openModal(modal) {
    if (modal) modal.hidden = false;
}

function closeModal(modal) {
    if (modal) modal.hidden = true;
}

document.querySelectorAll('[data-close-modal]').forEach((button) => {
    button.addEventListener('click', () => closeModal(document.querySelector(`#${button.dataset.closeModal}`)));
});

const addListingModal = document.querySelector('#add-listing-modal');
const openAddListing = document.querySelector('#open-add-listing');
if (openAddListing) openAddListing.addEventListener('click', () => openModal(addListingModal));

const listingCategory = document.querySelector('#listing-category');
const listingCondition = document.querySelector('#listing-condition');
if (listingCategory && listingCondition) {
    listingCategory.addEventListener('change', () => {
        const conditions = listingCategory.options[listingCategory.selectedIndex].text === 'Services' ? SERVICE_CONDITIONS : PRODUCT_CONDITIONS;
        listingCondition.replaceChildren(...conditions.map((condition) => new Option(condition, condition)));
    });
}

const listingImageInput = document.querySelector('#listing-image');
const listingImagePreview = document.querySelector('#add-listing-modal .image-preview');
const listingUploadBox = document.querySelector('#add-listing-modal .upload-box');
if (listingImageInput && listingImagePreview && listingUploadBox) {
    listingImageInput.addEventListener('change', () => {
        const [file] = listingImageInput.files;
        if (!file) return;
        listingImagePreview.src = URL.createObjectURL(file);
        listingImagePreview.hidden = false;
        listingUploadBox.hidden = true;
    });
}

const manageModal = document.querySelector('#manage-item-modal');
const manageForm = document.querySelector('#manage-listing-form');
const manageStatusBadge = document.querySelector('#manage-status-badge');
const manageImage = document.querySelector('#manage-image');
const manageViews = document.querySelector('#manage-views');
const manageName = document.querySelector('#manage-name');
const manageCategory = document.querySelector('#manage-category');
const managePrice = document.querySelector('#manage-price');
const manageCondition = document.querySelector('#manage-condition');
const manageLocation = document.querySelector('#manage-location');
const manageDescription = document.querySelector('#manage-description');
const manageStatus = document.querySelector('#manage-status');
const manageImageInput = document.querySelector('#manage-item-image');
let activeListingCard = null;

function refreshStatusAppearance() {
    if (!manageStatus || !manageStatusBadge) return;
    const status = manageStatus.value.toLowerCase();
    const label = manageStatus.options[manageStatus.selectedIndex].text;
    manageStatus.className = `status-select status-select-${status}`;
    manageStatusBadge.className = `status-pill status-pill-${status}`;
    manageStatusBadge.textContent = label;
}

document.querySelectorAll('.manage-button').forEach((button) => {
    button.addEventListener('click', () => {
        const card = button.closest('.seller-listing');
        if (!card || !manageForm) return;
        activeListingCard = card;
        manageForm.action = card.dataset.editUrl;
        manageImage.src = card.dataset.image;
        manageImage.alt = card.dataset.name;
        manageViews.textContent = card.dataset.views;
        manageName.value = card.dataset.name;
        manageCategory.value = card.dataset.categoryId;
        managePrice.value = card.dataset.price;
        manageLocation.value = card.dataset.location;
        manageDescription.value = card.dataset.description;
        manageStatus.value = card.dataset.statusValue;
        const conditions = card.dataset.category === 'Services' ? SERVICE_CONDITIONS : PRODUCT_CONDITIONS;
        manageCondition.replaceChildren(...conditions.map((condition) => new Option(condition, condition)));
        manageCondition.value = card.dataset.condition;
        refreshStatusAppearance();
        openModal(manageModal);
    });
});

if (window.initialManageListingId) {
    const initialCard = document.querySelector(`.seller-listing[data-edit-url*="/${window.initialManageListingId}/"]`);
    const initialButton = initialCard ? initialCard.querySelector('.manage-button') : null;
    if (initialButton) initialButton.click();
}

if (manageStatus) manageStatus.addEventListener('change', refreshStatusAppearance);
if (manageImageInput && manageImage) {
    manageImageInput.addEventListener('change', () => {
        const [file] = manageImageInput.files;
        if (file) manageImage.src = URL.createObjectURL(file);
    });
}

const deleteConfirmModal = document.querySelector('#delete-confirm-modal');
const deleteListingButton = document.querySelector('#delete-listing');
const deleteListingForm = document.querySelector('#delete-listing-form');
const cancelDeleteButton = document.querySelector('#cancel-delete');
if (deleteListingButton) {
    deleteListingButton.addEventListener('click', () => {
        if (activeListingCard && deleteListingForm) deleteListingForm.action = activeListingCard.dataset.deleteUrl;
        openModal(deleteConfirmModal);
    });
}
if (cancelDeleteButton) cancelDeleteButton.addEventListener('click', () => closeModal(deleteConfirmModal));

const listingSearch = document.querySelector('#listing-search');
const listingStatusFilter = document.querySelector('#listing-status-filter');
const noResults = document.querySelector('.no-filter-results');
function applyFilters() {
    const status = listingStatusFilter ? listingStatusFilter.value : 'all';
    const search = listingSearch ? listingSearch.value.trim().toLowerCase() : '';
    let visibleCount = 0;
    document.querySelectorAll('.seller-listing').forEach((card) => {
        const visible = (status === 'all' || card.dataset.status === status) && (!search || card.dataset.search.includes(search));
        card.hidden = !visible;
        if (visible) visibleCount += 1;
    });
    if (noResults) noResults.hidden = visibleCount > 0;
}
if (listingSearch) listingSearch.addEventListener('input', applyFilters);
if (listingStatusFilter) listingStatusFilter.addEventListener('change', applyFilters);
const listingFiltersForm = document.querySelector('#listing-filters');
if (listingFiltersForm) listingFiltersForm.addEventListener('submit', (event) => event.preventDefault());
