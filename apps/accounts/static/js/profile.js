const avatarInput = document.getElementById("avatar-input");
const avatarForm = document.getElementById("avatar-form");

if (avatarInput && avatarForm) {
    avatarInput.addEventListener("change", () => {
        if (avatarInput.files.length > 0) {
            avatarForm.submit();
        }
    });
}