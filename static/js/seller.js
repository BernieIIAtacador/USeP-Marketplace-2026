const listingFilters = document.querySelector('#listing-filters');

if (listingFilters) {
    const statusFilter = listingFilters.querySelector('[name="status"]');
    const searchInput = listingFilters.querySelector('[name="q"]');
    const listings = [...document.querySelectorAll('.seller-listing')];
    const noResults = document.querySelector('.no-filter-results');

    const filterListings = () => {
        const status = statusFilter.value.toLowerCase();
        const search = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        listings.forEach((listing) => {
            const matchesStatus = status === 'all' || listing.dataset.status === status;
            const matchesSearch = !search || listing.dataset.search.includes(search);
            const isVisible = matchesStatus && matchesSearch;
            listing.hidden = !isVisible;
            if (isVisible) visibleCount += 1;
        });

        if (noResults) noResults.hidden = visibleCount > 0;
    };

    listingFilters.addEventListener('submit', (event) => event.preventDefault());
    statusFilter.addEventListener('change', filterListings);
    searchInput.addEventListener('input', filterListings);
    filterListings();
}