const imageInput = document.querySelector('#item-image');
const imagePreview = document.querySelector('.preview-panel img');

if (imageInput && imagePreview) {
    imageInput.addEventListener('change', () => {
        const [file] = imageInput.files;
        if (file) {
            imagePreview.src = URL.createObjectURL(file);
        }
    });
}

const statusSelect = document.querySelector('#item-status');
const statusBadge = document.querySelector('#item-status-badge');
const statusSaveMessage = document.querySelector('#status-save-message');

if (statusSelect && statusBadge) {
    statusSelect.addEventListener('change', async () => {
        const selectedStatus = statusSelect.value;
        const formData = new FormData();
        formData.append('status', selectedStatus);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name="csrfmiddlewaretoken"]').value);

        statusSelect.disabled = true;
        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                credentials: 'same-origin',
            });
            if (!response.ok) throw new Error('Status update failed');

            const statusClass = selectedStatus.toLowerCase();
            statusSelect.className = `status-select status-select-${statusClass}`;
            statusBadge.className = `status-pill status-pill-${statusClass}`;
            statusBadge.textContent = selectedStatus;
            if (statusSaveMessage) statusSaveMessage.textContent = 'Status saved';
        } catch (error) {
            if (statusSaveMessage) statusSaveMessage.textContent = 'Could not save status';
        } finally {
            statusSelect.disabled = false;
        }
    });
}

const itemCategory = document.querySelector('#item-category');
const itemCondition = document.querySelector('#item-condition');

if (itemCategory && itemCondition) {
    const productConditions = ['Like new', 'Barely used', 'Good condition', 'For parts'];
    const serviceConditions = ['Available by appointment', 'On-site service', 'Currently unavailable'];

    itemCategory.addEventListener('change', () => {
        const conditions = itemCategory.value === 'Services' ? serviceConditions : productConditions;
        itemCondition.replaceChildren(...conditions.map((condition) => new Option(condition, condition)));
    });
}

const deleteButton = document.querySelector('#delete-listing');
const deleteModal = document.querySelector('#delete-modal');
const cancelDelete = document.querySelector('#cancel-delete');

if (deleteButton && deleteModal && cancelDelete) {
    deleteButton.addEventListener('click', () => {
        deleteModal.hidden = false;
    });
    cancelDelete.addEventListener('click', () => {
        deleteModal.hidden = true;
    });
}
