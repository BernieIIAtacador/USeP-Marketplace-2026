document.addEventListener('DOMContentLoaded', () => {
    const modal = document.querySelector('#detail-edit-modal');
    const openButton = document.querySelector('#open-detail-edit');
    const closeButtons = document.querySelectorAll('#close-detail-edit, #cancel-detail-edit');
    if (!modal || !openButton) return;

    const close = () => {
        modal.hidden = true;
    };

    openButton.addEventListener('click', () => {
        modal.hidden = false;
    });

    closeButtons.forEach((button) => button.addEventListener('click', close));
    modal.addEventListener('click', (event) => {
        if (event.target === modal) close();
    });
});
