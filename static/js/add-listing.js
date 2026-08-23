const listingImageInput = document.querySelector('#listing-image');
const listingImagePreview = document.querySelector('.image-preview');
const uploadBox = document.querySelector('.upload-box');

if (listingImageInput && listingImagePreview && uploadBox) {
    listingImageInput.addEventListener('change', () => {
        const [file] = listingImageInput.files;
        if (file) {
            listingImagePreview.src = URL.createObjectURL(file);
            listingImagePreview.hidden = false;
            uploadBox.hidden = true;
        }
    });
}

const listingCategory = document.querySelector('#listing-category');
const listingCondition = document.querySelector('#listing-condition');

if (listingCategory && listingCondition) {
    const productConditions = ['Like new', 'Barely used', 'Good condition', 'For parts'];
    const serviceConditions = ['Available by appointment', 'On-site service', 'Currently unavailable'];

    listingCategory.addEventListener('change', () => {
        const conditions = listingCategory.value === 'Services' ? serviceConditions : productConditions;
        listingCondition.replaceChildren(...conditions.map((condition) => new Option(condition, condition)));
    });
}
