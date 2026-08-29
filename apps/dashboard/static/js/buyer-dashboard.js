document.addEventListener('DOMContentLoaded', () => {
    const mainImage = document.querySelector('.detail-image');
    const thumbs = document.querySelectorAll('.thumb');

    if (mainImage && thumbs.length) {
        const updateMainImage = (src) => {
            mainImage.style.backgroundImage = `url('${src}')`;
            thumbs.forEach((thumb) => {
                const isActive = thumb.dataset.image === src;
                thumb.classList.toggle('active', isActive);
            });
        };

        thumbs.forEach((thumb) => {
            thumb.addEventListener('click', () => updateMainImage(thumb.dataset.image));
        });
    }

    const backToTopButton = document.getElementById('back-to-top');

    if (backToTopButton) {
        const toggleBackToTop = () => {
            if (window.scrollY > 400) {
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        };

        window.addEventListener('scroll', toggleBackToTop, { passive: true });
        backToTopButton.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        toggleBackToTop();
    }

    const savedKey = 'usep-marketplace-saved-items';

    const getSavedItems = () => {
        try {
            return JSON.parse(localStorage.getItem(savedKey) || '[]');
        } catch (error) {
            return [];
        }
    };

    const setSavedItems = (items) => {
        localStorage.setItem(savedKey, JSON.stringify(items));
        window.dispatchEvent(new CustomEvent('cart:updated', { detail: items }));
    };

    const refreshCartState = () => {
        syncSaveButtons();
        renderSavedItems();
    };

    const renderSavedItems = () => {
        const savedItems = getSavedItems();
        const savedList = document.getElementById('saved-items-list');
        const savedCount = document.getElementById('saved-count');
        const navbarCartBadge = document.getElementById('navbar-cart-badge');
        const cartPageList = document.getElementById('cart-page-items');

        if (savedCount) {
            savedCount.textContent = String(savedItems.length);
        }

        if (navbarCartBadge) {
            navbarCartBadge.textContent = String(savedItems.length);
        }

        if (savedList) {
            if (!savedItems.length) {
                savedList.innerHTML = '<p class="saved-empty">No saved items yet.</p>';
            } else {
                savedList.innerHTML = savedItems.map((item) => `
                    <div class="saved-item">
                        <div>
                            <strong>${item.title}</strong>
                            <small>${item.price}</small>
                        </div>
                        <button type="button" class="saved-remove" data-item-slug="${item.slug}">Remove</button>
                    </div>
                `).join('');
            }

            document.querySelectorAll('.saved-remove').forEach((button) => {
                button.addEventListener('click', () => {
                    const nextItems = getSavedItems().filter((item) => item.slug !== button.dataset.itemSlug);
                    setSavedItems(nextItems);
                    renderSavedItems();
                    syncSaveButtons();
                });
            });
        }

        if (cartPageList) {
            if (!savedItems.length) {
                cartPageList.innerHTML = `
                    <div class="empty-cart-state">
                        <h3>Your cart is empty.</h3>
                        <p>Save listings from the marketplace to see them here.</p>
                    </div>
                `;
                return;
            }

            cartPageList.innerHTML = savedItems.map((item) => `
                <article class="cart-item-card">
                    <div class="cart-item-details">
                        <h3>${item.title}</h3>
                        <p>${item.seller}</p>
                    </div>
                    <div class="cart-item-meta">
                        <strong>${item.price}</strong>
                        <div class="cart-item-actions">
                            <button type="button" class="mini-message-btn cart-message-btn" data-item-title="${item.title}" data-item-seller="${item.seller}">Message seller</button>
                            <button type="button" class="saved-remove cart-remove" data-item-slug="${item.slug}">Remove</button>
                        </div>
                    </div>
                </article>
            `).join('');

            document.querySelectorAll('.cart-remove').forEach((button) => {
                button.addEventListener('click', () => {
                    const nextItems = getSavedItems().filter((item) => item.slug !== button.dataset.itemSlug);
                    setSavedItems(nextItems);
                    renderSavedItems();
                    syncSaveButtons();
                });
            });

            document.querySelectorAll('.cart-message-btn').forEach((button) => {
                button.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    const title = button.dataset.itemTitle;
                    const seller = button.dataset.itemSeller;
                    alert(`Message to ${seller} about "${title}"`);
                });
            });
        }
    };

    const syncSaveButtons = () => {
        const savedItems = getSavedItems();
        const savedSlugs = new Set(savedItems.map((item) => item.slug));

        document.querySelectorAll('.save-btn').forEach((button) => {
            const isSaved = savedSlugs.has(button.dataset.itemSlug);
            button.classList.toggle('saved', isSaved);
            const icon = button.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-cart-check', isSaved);
                icon.classList.toggle('bi-cart3', !isSaved);
            }
        });

        document.querySelectorAll('.save-item-btn').forEach((button) => {
            const isSaved = savedSlugs.has(button.dataset.itemSlug);
            button.textContent = isSaved ? 'Added to cart' : 'Add to cart';
            button.classList.toggle('btn-success', isSaved);
            button.classList.toggle('btn-outline', !isSaved);
        });
    };

    const toggleSaveItem = (button) => {
        const slug = button.dataset.itemSlug;
        const title = button.dataset.itemTitle;
        const price = button.dataset.itemPrice;
        const seller = button.dataset.itemSeller;
        const savedItems = getSavedItems();
        const existingIndex = savedItems.findIndex((item) => item.slug === slug);

        if (existingIndex >= 0) {
            savedItems.splice(existingIndex, 1);
        } else {
            savedItems.push({ slug, title, price, seller });
        }

        setSavedItems(savedItems);
        renderSavedItems();
        syncSaveButtons();
    };

    document.querySelectorAll('.save-btn').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            toggleSaveItem(button);
        });
    });

    document.querySelectorAll('.save-item-btn').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            toggleSaveItem(button);
        });
    });

    document.querySelectorAll('.mini-message-btn').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            const title = button.dataset.itemTitle;
            const seller = button.dataset.itemSeller;
            alert(`Message to ${seller} about "${title}"`);
        });
    });

    window.addEventListener('pageshow', refreshCartState);
    window.addEventListener('storage', refreshCartState);
    window.addEventListener('cart:updated', refreshCartState);

    refreshCartState();
});
