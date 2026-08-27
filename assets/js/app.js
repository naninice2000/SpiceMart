/* ==========================================================================
   SpiceMart (FreshMarket) - Client-Side Application Logic
   ========================================================================== */

// ==========================================
    // CONFIGURATION KEYS
    // ==========================================
    const GOOGLE_CLIENT_ID = '460683061183-9el98nqfh0djo2qc215lcmb140ini306.apps.googleusercontent.com';
    const SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxpIlXam2h512fMHLeNY-_7AX_5ixidHIOBd_ND_RzerHVjONtBKMIJTWb-QZuHtNNm/exec'; // Products catalog & search
    const ORDERS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbxR3iwqfM0ya7XtBpUjQGFsjAEuSgge6h8Ea5PwDNB0992-y8r6ZcF2SPtdQpSTHBo9Tw/exec'; // Orders processing, Google Sheet storage, PDF invoice & email dispatch
    const CACHE_KEY = 'freshmarket_products_v3';
    const TAX_RATE = 0.0825; // 8.25% Sales Tax

    // Default Fallback Products Inventory
    const DEFAULT_PRODUCTS = [
      {
        id: 'p1',
        name: 'Alibaba Gold Basmati Rice',
        category: 'Rice & Grains',
        price: 18.99,
        quantity: '10 lbs Bag',
        inventory: 'In Stock',
        description: 'Extra long grain aged basmati rice with exquisite aroma and fluffy texture, ideal for biryani and daily meals.',
        image_url: 'assets/images/Alibaba Gold Basmati Rice.jpg'
      },
      {
        id: 'p2',
        name: 'Roshan Royal Basmati Rice',
        category: 'Rice & Grains',
        price: 21.50,
        quantity: '10 lbs Bag',
        inventory: 'In Stock',
        description: 'Premium quality naturally aged basmati rice known for its slender grains and distinctive fragrance.',
        image_url: 'assets/images/Roshan Basmati Rice.jpg'
      },
      {
        id: 'p3',
        name: 'Whole Black Cardamom',
        category: 'Spices',
        price: 6.49,
        quantity: '200g Pack',
        inventory: 'In Stock',
        description: 'Smoky, intensely aromatic whole black cardamom pods sourced directly from Himalayan organic farms.',
        image_url: 'assets/images/Black Cardamom.jpg'
      },
      {
        id: 'p4',
        name: 'Whole Black Peppercorns',
        category: 'Spices',
        price: 4.99,
        quantity: '250g Jar',
        inventory: 'In Stock',
        description: 'Bold Malabar grade whole black peppercorns offering robust heat and sharp citrusy bite.',
        image_url: 'assets/images/Black Pepper.jpg'
      },
      {
        id: 'p5',
        name: 'Organic Whole Turmeric',
        category: 'Spices',
        price: 5.25,
        quantity: '300g Pack',
        inventory: 'In Stock',
        description: 'Sun-dried pure whole turmeric fingers with high curcumin content and rich golden hue.',
        image_url: 'assets/images/Whole Turmeric.jpg'
      },
      {
        id: 'p6',
        name: 'Kasuri Fenugreek Leaves',
        category: 'Herbs & Leaves',
        price: 3.75,
        quantity: '100g Box',
        inventory: 'In Stock',
        description: 'Fragrant shade-dried fenugreek leaves that bring rich savory aroma to curries and breads.',
        image_url: 'assets/images/Fenugreek Leaves.jpg'
      },
      {
        id: 'p7',
        name: 'Fresh Dried Rosemary',
        category: 'Herbs & Leaves',
        price: 4.20,
        quantity: '150g Jar',
        inventory: 'In Stock',
        description: 'Aromatic needle-leaf dried rosemary herbs perfect for roasted potatoes, soups, and marinades.',
        image_url: 'assets/images/Rosemary.jpg'
      }
    ];

    function normalizeProduct(item, idx) {
      if (!item) return null;
      return {
        id: String(item.id ?? item.ID ?? item.item_id ?? item.itemId ?? `p_${idx + 1}`),
        name: String(item.name ?? item.Name ?? item.title ?? item.Title ?? 'Grocery Item'),
        price: Number(item.price ?? item.Price ?? 0),
        category: String(item.category ?? item.Category ?? 'General'),
        quantity: String(item.quantity ?? item.Quantity ?? item.unit ?? item.Unit ?? '1 Unit'),
        inventory: String(item.inventory ?? item.Inventory ?? item.stock ?? item.Stock ?? 'In Stock'),
        description: String(item.description ?? item.Description ?? ''),
        image_url: String(item.image_url ?? item.Image_URL ?? item.image ?? item.Image ?? '')
      };
    }

    let allProducts = DEFAULT_PRODUCTS.map(normalizeProduct);
    let selectedCategory = 'All';
    let cart = [];
    try {
      const parsedCart = JSON.parse(localStorage.getItem('user_cart') || '[]');
      if (Array.isArray(parsedCart)) {
        cart = parsedCart.map(it => ({
          id: String(it.id),
          name: String(it.name || 'Item'),
          price: Number(it.price || 0),
          qty: parseInt(it.qty, 10) || 1
        }));
      }
    } catch (e) {
      cart = [];
    }
    let localQtyState = {}; 
    let currentUser = JSON.parse(localStorage.getItem('user_google_profile') || 'null');
    let currentPage = 'home';
    let searchQuery = '';
    let searchDebounceTimer = null;
    let isSearchingRemote = false;

    // Decode Google JWT Token
    function parseJwt(token) {
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
      } catch (err) {
        console.error('Failed to parse JWT payload', err);
        return null;
      }
    }

    // Google Sign-In Callback Handler
    function handleCredentialResponse(response) {
      const payload = parseJwt(response.credential);
      if (!payload) return;

      currentUser = {
        name: payload.name || 'Customer',
        email: payload.email || '',
        picture: payload.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(payload.name || 'Customer')}&background=059669&color=fff`
      };
      localStorage.setItem('user_google_profile', JSON.stringify(currentUser));
      renderAuthUI();
      populateCheckoutProfile();
    }

    // Initialize Google Identity Services buttons (Header + Checkout banner)
    function initGoogleAuth() {
      if (!window.google || !google.accounts || !google.accounts.id) return;

      if (GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com') {
        try {
          google.accounts.id.initialize({
            client_id: GOOGLE_CLIENT_ID,
            callback: handleCredentialResponse,
            auto_select: false
          });

          // 1. Render in top navigation header
          const navBtnContainer = document.getElementById('g_id_signin_btn');
          if (navBtnContainer) {
            google.accounts.id.renderButton(navBtnContainer, {
              theme: 'outline',
              size: 'small',
              shape: 'pill'
            });
          }

          // 2. Render inside checkout page warning banner
          const checkoutBtnContainer = document.getElementById('checkout-g-btn-wrapper');
          if (checkoutBtnContainer && !currentUser) {
            checkoutBtnContainer.innerHTML = `<div id="g_id_checkout_btn"></div>`;
            google.accounts.id.renderButton(
              document.getElementById('g_id_checkout_btn'),
              { theme: 'filled_blue', size: 'large', shape: 'pill', width: 250 }
            );
          }
        } catch (e) {
          console.warn('Google Auth initialization error:', e);
        }
      }
    }

    // Render Auth UI in Header with Referrer Policy and Fallbacks
    function renderAuthUI() {
      const authContainer = document.getElementById('auth-container');
      if (currentUser) {
        const avatarUrl = currentUser.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=059669&color=fff`;
        authContainer.innerHTML = `
          <div class="flex items-center gap-2 bg-gray-50 border border-gray-200/80 px-2 py-1 rounded-full shadow-2xs">
            <img 
              src="${avatarUrl}" 
              referrerpolicy="no-referrer"
              onerror="this.src='https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=059669&color=fff'"
              class="w-7 h-7 rounded-full border border-emerald-400 object-cover" 
              title="${currentUser.email}" 
              alt="${currentUser.name}" 
            />
            <span class="text-xs font-semibold text-gray-700 hidden sm:inline max-w-[100px] truncate">${currentUser.name}</span>
            <button onclick="logout()" class="text-[11px] text-gray-400 hover:text-red-600 font-medium ml-0.5 transition" title="Sign Out">
              <i class="fa-solid fa-arrow-right-from-bracket"></i>
            </button>
          </div>
        `;
      } else {
        authContainer.innerHTML = `<div id="g_id_signin_btn"></div>`;
        initGoogleAuth();
      }
    }

    function logout() {
      currentUser = null;
      localStorage.removeItem('user_google_profile');
      renderAuthUI();
      populateCheckoutProfile();
      if (window.google && google.accounts && google.accounts.id) {
        google.accounts.id.disableAutoSelect();
      }
    }

    // App Lifecycle
    async function init() {
      renderAuthUI();
      
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          if (Array.isArray(parsed) && parsed.length > 0) {
            allProducts = parsed.map(normalizeProduct).filter(Boolean);
          }
        } catch (e) {
          console.error(e);
        }
      }

      renderCategories();
      renderProducts();
      renderCart();

      // Silent background catalog sync
      if (SCRIPT_URL && SCRIPT_URL.startsWith('https://')) {
        try {
          const res = await fetch(SCRIPT_URL);
          const freshData = await res.json();
          if (Array.isArray(freshData) && freshData.length > 0) {
            allProducts = freshData.map(normalizeProduct).filter(Boolean);
            localStorage.setItem(CACHE_KEY, JSON.stringify(allProducts));
            renderCategories();
            renderProducts();
            renderCart();
          }
        } catch (err) {
          console.warn('Backend sync note (using cached products):', err);
        }
      }
    }

    // Single Page Navigation
    function navigate(pageId) {
      currentPage = pageId;
      ['home', 'products', 'contact', 'checkout'].forEach(p => {
        const el = document.getElementById(`page-${p}`);
        if (el) el.classList.add('hidden');
      });
      
      const target = document.getElementById(`page-${pageId}`);
      if (target) target.classList.remove('hidden');
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Update Desktop Nav Active States
      ['home', 'products', 'contact'].forEach(p => {
        const deskBtn = document.getElementById(`desk-nav-${p}`);
        if (deskBtn) {
          if (p === pageId) {
            deskBtn.className = 'desk-nav-btn font-bold text-emerald-600 hover:text-emerald-700 transition';
          } else {
            deskBtn.className = 'desk-nav-btn font-medium text-gray-600 hover:text-emerald-600 transition';
          }
        }
      });

      // Update Mobile Nav Active States
      ['home', 'products', 'contact'].forEach(p => {
        const mobBtn = document.getElementById(`mob-nav-${p}`);
        if (mobBtn) {
          if (p === pageId) {
            mobBtn.className = 'mob-nav-btn flex flex-col items-center justify-center flex-1 py-1 text-emerald-600 active:scale-95 transition';
            const span = mobBtn.querySelector('span');
            if (span) span.className = 'text-[10px] font-black mt-1 tracking-tight';
          } else {
            mobBtn.className = 'mob-nav-btn flex flex-col items-center justify-center flex-1 py-1 text-gray-500 hover:text-emerald-600 active:scale-95 transition';
            const span = mobBtn.querySelector('span');
            if (span) span.className = 'text-[10px] font-medium mt-1 tracking-tight';
          }
        }
      });

      renderCart();

      if (pageId === 'checkout') {
        populateCheckoutProfile();
        renderCheckoutSummary();
      }
    }

    // Categories
    function renderCategories() {
      const categories = ['All', ...new Set(allProducts.map(p => p.category).filter(Boolean))];
      
      const tabs = document.getElementById('category-tabs');
      tabs.innerHTML = categories.map(cat => {
        const isActive = selectedCategory === cat;
        return `
          <button onclick="filterCategory('${cat}')" 
            class="cat-pill whitespace-nowrap px-4 py-2 rounded-full text-xs sm:text-sm font-bold transition active:scale-95 flex-shrink-0 cursor-pointer ${
              isActive ? 'bg-emerald-600 text-white shadow-xs' : 'bg-gray-200/90 text-gray-700 hover:bg-emerald-50 hover:text-emerald-700'
            }">
            ${cat === 'All' ? 'All Products' : cat}
          </button>
        `;
      }).join('');

      const homeCats = document.getElementById('home-categories-grid');
      const iconMap = {
        'Rice & Grains': 'fa-bowl-rice',
        'Spices': 'fa-pepper-hot',
        'Herbs & Leaves': 'fa-seedling',
        'Groceries': 'fa-basket-shopping'
      };

      homeCats.innerHTML = categories.filter(c => c !== 'All').map(cat => {
        const icon = iconMap[cat] || 'fa-basket-shopping';
        return `
          <div onclick="selectAndNavigateCategory('${cat}')" class="bg-white border border-gray-200/90 rounded-2xl p-4 sm:p-5 text-center cursor-pointer shadow-xs active:scale-98 hover:shadow-md hover:border-emerald-400 transition group flex flex-col items-center justify-center">
            <div class="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-2.5 sm:mb-3 text-xl group-hover:scale-110 group-hover:bg-emerald-600 group-hover:text-white transition duration-200">
              <i class="fa-solid ${icon}"></i>
            </div>
            <h4 class="font-bold text-xs sm:text-sm text-gray-800 group-hover:text-emerald-700 transition">${cat}</h4>
          </div>
        `;
      }).join('');
    }

    // Search Engine
    function matchProduct(prod, query) {
      if (!prod || !query) return false;
      const q = query.toLowerCase().trim();
      const name = (prod.name || '').toLowerCase();
      const category = (prod.category || '').toLowerCase();
      const description = (prod.description || '').toLowerCase();
      const quantity = (prod.quantity || '').toLowerCase();
      return name.includes(q) || category.includes(q) || description.includes(q) || quantity.includes(q);
    }

    function onSearchInput(val) {
      const q = val.trim();
      const deskInput = document.getElementById('desktop-search-input');
      const mobInput = document.getElementById('mobile-search-input');
      if (deskInput && deskInput.value !== val) deskInput.value = val;
      if (mobInput && mobInput.value !== val) mobInput.value = val;

      document.querySelectorAll('.search-clear-btn').forEach(btn => {
        if (q.length > 0) btn.classList.remove('hidden');
        else btn.classList.add('hidden');
      });

      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);

      if (q.length === 0) {
        clearSearch();
        return;
      }

      searchDebounceTimer = setTimeout(() => {
        executeSearch(q);
      }, 250);
    }

    function handleSearchKeydown(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
        executeSearch(e.target.value.trim());
      }
    }

    async function executeSearch(query) {
      if (!query || query.trim() === '') {
        clearSearch();
        return;
      }

      searchQuery = query.trim();
      const lowerQ = searchQuery.toLowerCase();

      if (currentPage !== 'products') {
        navigate('products');
      }

      const localMatches = allProducts.filter(p => matchProduct(p, lowerQ));

      const banner = document.getElementById('search-results-banner');
      const queryDisplay = document.getElementById('search-query-display');
      const matchCount = document.getElementById('search-match-count');
      const loadingBanner = document.getElementById('search-loading-banner');
      const categoryTabs = document.getElementById('category-tabs-container');

      if (categoryTabs) categoryTabs.classList.add('hidden');

      if (localMatches.length > 0) {
        if (loadingBanner) loadingBanner.classList.add('hidden');
        if (banner) {
          banner.classList.remove('hidden');
          if (queryDisplay) queryDisplay.innerText = `"${searchQuery}"`;
          if (matchCount) matchCount.innerText = localMatches.length;
        }
        renderFilteredProducts(localMatches);
        return;
      }

      // Online Apps Script Search Fallback
      if (SCRIPT_URL && SCRIPT_URL.startsWith('https://') && searchQuery.length >= 2) {
        setSearchLoadingState(true);
        if (banner) banner.classList.add('hidden');
        if (loadingBanner) loadingBanner.classList.remove('hidden');

        try {
          const searchUrl = SCRIPT_URL.includes('?') 
            ? `${SCRIPT_URL}&q=${encodeURIComponent(searchQuery)}` 
            : `${SCRIPT_URL}?q=${encodeURIComponent(searchQuery)}`;

          const res = await fetch(searchUrl);
          const freshData = await res.json();

          if (Array.isArray(freshData) && freshData.length > 0) {
            const normalizedFresh = freshData.map(normalizeProduct).filter(Boolean);
            const existingIds = new Set(allProducts.map(p => p.id));
            let addedCount = 0;
            normalizedFresh.forEach(item => {
              if (!existingIds.has(item.id)) {
                allProducts.push(item);
                existingIds.add(item.id);
                addedCount++;
              }
            });

            if (addedCount > 0) {
              localStorage.setItem(CACHE_KEY, JSON.stringify(allProducts));
              renderCategories();
            }

            const remoteMatches = allProducts.filter(p => matchProduct(p, lowerQ));
            setSearchLoadingState(false);
            if (loadingBanner) loadingBanner.classList.add('hidden');

            if (remoteMatches.length > 0) {
              if (banner) {
                banner.classList.remove('hidden');
                if (queryDisplay) queryDisplay.innerText = `"${searchQuery}"`;
                if (matchCount) matchCount.innerText = remoteMatches.length;
              }
              renderFilteredProducts(remoteMatches);
              return;
            }
          }
        } catch (err) {
          console.warn('Apps Script search error:', err);
        }

        setSearchLoadingState(false);
        if (loadingBanner) loadingBanner.classList.add('hidden');
      }

      if (banner) {
        banner.classList.remove('hidden');
        if (queryDisplay) queryDisplay.innerText = `"${searchQuery}"`;
        if (matchCount) matchCount.innerText = 0;
      }
      renderFilteredProducts([], `No products matching "${searchQuery}" found in catalog.`);
    }

    function setSearchLoadingState(isLoading) {
      isSearchingRemote = isLoading;
      document.querySelectorAll('.search-icon').forEach(el => {
        if (isLoading) el.classList.add('hidden');
        else el.classList.remove('hidden');
      });
      document.querySelectorAll('.search-spinner').forEach(el => {
        if (isLoading) el.classList.remove('hidden');
        else el.classList.add('hidden');
      });
    }

    function clearSearch() {
      searchQuery = '';
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
      setSearchLoadingState(false);

      const deskInput = document.getElementById('desktop-search-input');
      const mobInput = document.getElementById('mobile-search-input');
      if (deskInput) deskInput.value = '';
      if (mobInput) mobInput.value = '';

      document.querySelectorAll('.search-clear-btn').forEach(btn => btn.classList.add('hidden'));

      const banner = document.getElementById('search-results-banner');
      if (banner) banner.classList.add('hidden');

      const loadingBanner = document.getElementById('search-loading-banner');
      if (loadingBanner) loadingBanner.classList.add('hidden');

      const categoryTabs = document.getElementById('category-tabs-container');
      if (categoryTabs) categoryTabs.classList.remove('hidden');

      renderProducts();
    }

    function selectAndNavigateCategory(cat) {
      clearSearch();
      filterCategory(cat);
      navigate('products');
    }

    function filterCategory(cat) {
      if (searchQuery) {
        clearSearch();
      }
      selectedCategory = cat;
      renderCategories();
      renderProducts();
    }

    // Products Grid
    function renderProducts() {
      const filtered = selectedCategory === 'All' 
        ? allProducts 
        : allProducts.filter(p => p.category === selectedCategory);

      renderFilteredProducts(filtered);
    }

    function renderFilteredProducts(productsList, customEmptyMsg) {
      const grid = document.getElementById('products-grid');
      const empty = document.getElementById('empty-notice');
      const emptyTitle = document.getElementById('empty-title');
      const emptyDesc = document.getElementById('empty-desc');

      if (!productsList || productsList.length === 0) {
        grid.innerHTML = '';
        if (emptyTitle) emptyTitle.innerText = 'No matches found';
        if (emptyDesc) emptyDesc.innerText = customEmptyMsg || `We couldn't find any products matching this selection.`;
        empty.classList.remove('hidden');
        return;
      }

      empty.classList.add('hidden');
      grid.innerHTML = productsList.map(prod => {
        const safeId = String(prod.id);
        const qty = localQtyState[safeId] || 1;
        const imgBlock = prod.image_url 
          ? `<img src="${prod.image_url}" alt="${prod.name}" loading="lazy" onerror="this.outerHTML='<div class=\\'w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 text-xs italic\\'>No Image</div>'" class="w-full h-full object-cover cursor-pointer group-hover:scale-105 transition duration-300" onclick="openModal('${safeId}')" />`
          : `<div onclick="openModal('${safeId}')" class="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400 text-xs italic cursor-pointer">No Image</div>`;

        return `
          <div class="bg-white rounded-2xl border border-gray-200/80 shadow-xs overflow-hidden flex flex-col justify-between hover:shadow-md transition duration-200 group">
            
            <div class="relative aspect-square w-full bg-gray-100 overflow-hidden">
              ${imgBlock}
              <span class="absolute top-2 left-2 bg-emerald-700/80 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                ${prod.category || 'General'}
              </span>
            </div>

            <div class="p-3 sm:p-4 flex flex-col flex-grow justify-between">
              <div>
                <h3 class="font-bold text-xs sm:text-sm text-gray-900 cursor-pointer line-clamp-2 leading-snug hover:text-emerald-600 transition" onclick="openModal('${safeId}')">
                  ${prod.name}
                </h3>
                <div class="text-[11px] text-gray-500 mt-1">${prod.quantity || '1 Unit'}</div>
                <div class="font-black text-sm sm:text-base text-emerald-700 mt-1.5">$${Number(prod.price || 0).toFixed(2)}</div>
              </div>

              <div class="mt-3 pt-2.5 border-t border-gray-100">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-[11px] font-semibold text-gray-500">Qty:</span>
                  <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-gray-50 shadow-2xs">
                    <button onclick="updateLocalQty('${safeId}', -1)" aria-label="Decrease quantity" class="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center text-gray-700 hover:bg-gray-200 active:bg-gray-300 font-bold transition">-</button>
                    <span id="qty-${safeId}" class="w-7 sm:w-8 text-center text-xs font-bold text-gray-900 bg-white">${qty}</span>
                    <button onclick="updateLocalQty('${safeId}', 1)" aria-label="Increase quantity" class="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center text-gray-700 hover:bg-gray-200 active:bg-gray-300 font-bold transition">+</button>
                  </div>
                </div>
                
                <button id="add-btn-${safeId}" onclick="handleAddToCartClick(this, '${safeId}')" class="w-full bg-emerald-600 text-white py-2 sm:py-2.5 rounded-xl font-bold hover:bg-emerald-700 active:scale-95 text-xs sm:text-sm flex items-center justify-center gap-1.5 shadow-xs transition">
                  <i class="fa-solid fa-cart-plus text-xs"></i> <span>Add to Cart</span>
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function updateLocalQty(prodId, delta) {
      const safeId = String(prodId);
      const current = parseInt(localQtyState[safeId], 10) || 1;
      const next = Math.max(1, current + delta);
      localQtyState[safeId] = next;
      const el = document.getElementById(`qty-${safeId}`);
      if (el) el.innerText = next;
    }

    // Modal Details
    function openModal(prodId) {
      const safeId = String(prodId);
      const prod = allProducts.find(p => String(p.id) === safeId);
      if (!prod) return;

      const imgBlock = prod.image_url 
        ? `<img src="${prod.image_url}" alt="${prod.name}" class="w-full h-48 sm:h-60 object-cover rounded-2xl mb-4 shadow-xs" />`
        : `<div class="w-full h-40 bg-gray-100 flex items-center justify-center text-gray-400 text-sm italic rounded-2xl mb-4">No Image Available</div>`;

      document.getElementById('modal-content').innerHTML = `
        ${imgBlock}
        <div class="flex items-center gap-2 mb-1">
          <span class="text-[10px] sm:text-xs font-bold bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">${prod.category || 'General'}</span>
          <span class="text-xs text-gray-500">Unit: ${prod.quantity || 'Standard'}</span>
        </div>
        <h2 class="text-xl sm:text-2xl font-black text-gray-900 leading-snug mt-1">${prod.name}</h2>
        <div class="text-2xl font-black text-emerald-700 my-2">$${Number(prod.price || 0).toFixed(2)}</div>
        <p class="text-gray-600 text-xs sm:text-sm leading-relaxed mb-6">${prod.description || 'No detailed description available for this item.'}</p>
        <button onclick="handleAddToCartClick(this, '${safeId}'); closeModal();" class="w-full bg-emerald-600 text-white py-3.5 rounded-xl font-black text-base hover:bg-emerald-700 active:scale-98 transition shadow-md flex items-center justify-center gap-2">
          <i class="fa-solid fa-cart-plus"></i> <span>Add to Cart</span>
        </button>
      `;
      document.getElementById('product-modal').classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    }

    function closeModal() {
      document.getElementById('product-modal').classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }

    function handleModalBackdropClick(e) {
      if (e.target.id === 'product-modal') {
        closeModal();
      }
    }

    function handleAddToCartClick(btnEl, prodId) {
      addToCart(prodId);
      if (btnEl) {
        const origContent = btnEl.innerHTML;
        btnEl.innerHTML = `<i class="fa-solid fa-check text-xs"></i> <span>Added!</span>`;
        btnEl.classList.add('bg-emerald-800');
        setTimeout(() => {
          btnEl.innerHTML = origContent;
          btnEl.classList.remove('bg-emerald-800');
        }, 800);
      }
    }

    // Cart Operations
    function addToCart(prodId) {
      const safeId = String(prodId);
      const prod = allProducts.find(p => String(p.id) === safeId);
      if (!prod) return;

      const qtyToAdd = parseInt(localQtyState[safeId], 10) || 1;
      const existing = cart.find(item => String(item.id) === safeId);

      if (existing) {
        existing.qty = (parseInt(existing.qty, 10) || 0) + qtyToAdd;
      } else {
        cart.push({
          id: safeId,
          name: prod.name,
          price: Number(prod.price || 0),
          qty: qtyToAdd
        });
      }

      localQtyState[safeId] = 1;
      const el = document.getElementById(`qty-${safeId}`);
      if (el) el.innerText = '1';

      saveCart();
      renderCart();

      const badge = document.getElementById('cart-badge');
      const mobBadge = document.getElementById('mob-cart-badge');
      [badge, mobBadge].forEach(b => {
        if (b) {
          b.classList.remove('scale-125', 'bg-amber-500');
          void b.offsetWidth;
          b.classList.add('scale-125', 'bg-amber-500');
          setTimeout(() => {
            b.classList.remove('scale-125', 'bg-amber-500');
          }, 300);
        }
      });

      try {
        if (window.navigator && window.navigator.vibrate) {
          window.navigator.vibrate(40);
        }
      } catch (e) {}
    }

    function updateCartItemQty(index, delta) {
      if (!cart[index]) return;
      const newQty = (parseInt(cart[index].qty, 10) || 0) + delta;
      if (newQty <= 0) {
        cart.splice(index, 1);
      } else {
        cart[index].qty = newQty;
      }
      saveCart();
      renderCart();
      if (currentPage === 'checkout') {
        renderCheckoutSummary();
      }
    }

    function removeFromCart(index) {
      cart.splice(index, 1);
      saveCart();
      renderCart();
      if (currentPage === 'checkout') {
        renderCheckoutSummary();
      }
    }

    function saveCart() {
      localStorage.setItem('user_cart', JSON.stringify(cart));
    }

    function getTaxRateDisplay() {
      return `${(TAX_RATE * 100).toFixed(2).replace(/\.00$/, '')}%`;
    }

    function getCartSubtotal() {
      return cart.reduce((sum, item) => sum + (Number(item.price || 0) * (parseInt(item.qty, 10) || 1)), 0);
    }

    function getCartTax(subtotal) {
      const sub = typeof subtotal === 'number' ? subtotal : getCartSubtotal();
      return sub * TAX_RATE;
    }

    function getCartTotal() {
      const subtotal = getCartSubtotal();
      const tax = getCartTax(subtotal);
      return subtotal + tax;
    }

    function renderCart() {
      const cartItemsEl = document.getElementById('cart-items');
      const cartSubtotalEl = document.getElementById('cart-subtotal');
      const cartTaxRateEl = document.getElementById('cart-tax-rate-label');
      const cartTaxEl = document.getElementById('cart-tax');
      const cartTotalEl = document.getElementById('cart-total');
      const badge = document.getElementById('cart-badge');
      const mobBadge = document.getElementById('mob-cart-badge');
      const floatingBar = document.getElementById('mobile-floating-cart-bar');
      const floatingCount = document.getElementById('floating-cart-count');
      const floatingTotal = document.getElementById('floating-cart-total');

      const totalCount = cart.reduce((sum, item) => sum + (parseInt(item.qty, 10) || 1), 0);
      const subtotal = getCartSubtotal();
      const tax = getCartTax(subtotal);
      const grandTotal = subtotal + tax;

      if (badge) badge.innerText = totalCount;
      if (mobBadge) mobBadge.innerText = totalCount;
      if (cartTaxRateEl) cartTaxRateEl.innerText = getTaxRateDisplay();

      if (floatingCount) floatingCount.innerText = totalCount;
      if (floatingTotal) floatingTotal.innerText = `$${grandTotal.toFixed(2)}`;
      if (floatingBar) {
        if (totalCount > 0 && (currentPage === 'home' || currentPage === 'products')) {
          floatingBar.classList.remove('hidden');
        } else {
          floatingBar.classList.add('hidden');
        }
      }

      if (cart.length === 0) {
        cartItemsEl.innerHTML = `
          <div class="text-center py-12 px-4">
            <div class="w-14 h-14 bg-gray-100 text-gray-400 rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">
              <i class="fa-solid fa-basket-shopping"></i>
            </div>
            <p class="text-gray-500 font-medium text-sm">Your cart is currently empty.</p>
            <p class="text-xs text-gray-400 mt-1">Add items from the store to begin checkout.</p>
          </div>
        `;
        if (cartSubtotalEl) cartSubtotalEl.innerText = '$0.00';
        if (cartTaxEl) cartTaxEl.innerText = '$0.00';
        if (cartTotalEl) cartTotalEl.innerText = '$0.00';
        return;
      }

      cartItemsEl.innerHTML = cart.map((item, index) => {
        const itemTotal = Number(item.price) * parseInt(item.qty, 10);

        return `
          <div class="flex items-center justify-between border-b border-gray-100 pb-3 pt-1">
            <div class="flex-1 pr-2 min-w-0">
              <h5 class="font-bold text-xs sm:text-sm text-gray-800 leading-snug truncate">${item.name}</h5>
              <div class="text-[11px] text-gray-500 mt-0.5">$${Number(item.price).toFixed(2)} each</div>
            </div>
            
            <div class="flex items-center border border-gray-200 rounded-lg bg-gray-50 mr-2.5 shadow-2xs">
              <button onclick="updateCartItemQty(${index}, -1)" aria-label="Reduce" class="w-7 h-7 flex items-center justify-center text-gray-700 hover:bg-gray-200 active:bg-gray-300 text-xs font-bold transition">-</button>
              <span class="w-6 text-center text-xs font-bold text-gray-800 bg-white">${item.qty}</span>
              <button onclick="updateCartItemQty(${index}, 1)" aria-label="Increase" class="w-7 h-7 flex items-center justify-center text-gray-700 hover:bg-gray-200 active:bg-gray-300 text-xs font-bold transition">+</button>
            </div>

            <div class="flex items-center gap-2">
              <span class="font-black text-xs sm:text-sm text-gray-900 min-w-[45px] text-right">$${itemTotal.toFixed(2)}</span>
              <button onclick="removeFromCart(${index})" aria-label="Delete item" class="w-8 h-8 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 flex items-center justify-center active:scale-95 transition">
                <i class="fa-solid fa-trash-can text-xs"></i>
              </button>
            </div>
          </div>
        `;
      }).join('');

      if (cartSubtotalEl) cartSubtotalEl.innerText = `$${subtotal.toFixed(2)}`;
      if (cartTaxEl) cartTaxEl.innerText = `$${tax.toFixed(2)}`;
      if (cartTotalEl) cartTotalEl.innerText = `$${grandTotal.toFixed(2)}`;
    }

    function toggleCartDrawer() {
      const drawer = document.getElementById('cart-drawer');
      const backdrop = document.getElementById('cart-drawer-backdrop');
      
      const isOpen = !drawer.classList.contains('translate-x-full');
      if (isOpen) {
        drawer.classList.add('translate-x-full');
        backdrop.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
      } else {
        drawer.classList.remove('translate-x-full');
        backdrop.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
      }
    }

    // Checkout
    function goToCheckoutPage() {
      if (cart.length === 0) {
        alert('Your cart is empty! Add products before checking out.');
        return;
      }
      toggleCartDrawer();
      navigate('checkout');
    }

    function populateCheckoutProfile() {
      const authWarning = document.getElementById('checkout-auth-warning');
      const mainView = document.getElementById('checkout-main-view');

      if (!currentUser) {
        if (authWarning) authWarning.classList.remove('hidden');
        if (mainView) mainView.classList.add('opacity-40', 'pointer-events-none');
        initGoogleAuth();
        return;
      }

      if (authWarning) authWarning.classList.add('hidden');
      if (mainView) mainView.classList.remove('opacity-40', 'pointer-events-none');

      const avatar = document.getElementById('checkout-avatar');
      const dispName = document.getElementById('checkout-display-name');
      const dispEmail = document.getElementById('checkout-display-email');
      const inputName = document.getElementById('cust-name-input');
      const inputEmail = document.getElementById('cust-email-input');

      if (avatar) {
        avatar.src = currentUser.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.name)}&background=059669&color=fff`;
      }
      if (dispName) dispName.innerText = currentUser.name;
      if (dispEmail) dispEmail.innerText = currentUser.email;
      if (inputName) inputName.value = currentUser.name;
      if (inputEmail) inputEmail.value = currentUser.email;
    }

    function renderCheckoutSummary() {
      const itemsList = document.getElementById('checkout-items-list');
      const subtotalEl = document.getElementById('checkout-subtotal');
      const taxRateLabelEl = document.getElementById('checkout-tax-rate-label');
      const taxEl = document.getElementById('checkout-tax');
      const totalEl = document.getElementById('checkout-total');

      if (taxRateLabelEl) taxRateLabelEl.innerText = getTaxRateDisplay();

      if (cart.length === 0) {
        if (itemsList) itemsList.innerHTML = '<p class="text-xs text-gray-400 text-center py-4">No items selected.</p>';
        if (subtotalEl) subtotalEl.innerText = '$0.00';
        if (taxEl) taxEl.innerText = '$0.00';
        if (totalEl) totalEl.innerText = '$0.00';
        return;
      }

      const subtotal = getCartSubtotal();
      const tax = getCartTax(subtotal);
      const grandTotal = subtotal + tax;

      if (itemsList) {
        itemsList.innerHTML = cart.map(item => `
          <div class="flex justify-between items-center text-xs py-1 border-b border-gray-50">
            <div class="truncate mr-2">
              <span class="font-semibold text-gray-800">${item.name}</span>
              <span class="text-gray-400"> (x${item.qty})</span>
            </div>
            <span class="font-bold text-gray-900 flex-shrink-0">$${(Number(item.price) * parseInt(item.qty, 10)).toFixed(2)}</span>
          </div>
        `).join('');
      }

      if (subtotalEl) subtotalEl.innerText = `$${subtotal.toFixed(2)}`;
      if (taxEl) taxEl.innerText = `$${tax.toFixed(2)}`;
      if (totalEl) totalEl.innerText = `$${grandTotal.toFixed(2)}`;
    }

    function handleAddressTypeChange() {
      const type = document.getElementById('cust-addr-type-input').value;
      const bGroup = document.getElementById('business-name-group');
      const bInput = document.getElementById('cust-business-name-input');
      if (type === 'Commercial') {
        bGroup.classList.remove('hidden');
        bInput.required = true;
      } else {
        bGroup.classList.add('hidden');
        bInput.required = false;
      }
    }

    // Submit Order Action (Google Sheet storage + PDF invoice email)
    async function submitCheckoutOrder(e) {
      e.preventDefault();

      if (!currentUser) {
        alert('Please sign in with your Google Account before placing the order.');
        return;
      }

      if (cart.length === 0) {
        alert('Cart is empty.');
        return;
      }

      const submitBtn = e.target.querySelector('button[type="submit"]');
      const origBtnHtml = submitBtn ? submitBtn.innerHTML : '';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-base"></i> <span>Processing & Generating Invoice...</span>`;
      }

      const orderId = 'ORD-' + Math.floor(100000 + Math.random() * 900000);
      const isBusiness = document.getElementById('cust-addr-type-input').value === 'Commercial';
      const bName = isBusiness ? document.getElementById('cust-business-name-input').value : '';
      const street = document.getElementById('cust-street-input').value;
      const city = document.getElementById('cust-city-input').value;
      const state = document.getElementById('cust-state-input').value;
      const zip = document.getElementById('cust-zip-input').value;
      const phone = document.getElementById('cust-phone-input').value;
      const fullAddress = `${street}, ${city}, ${state} ${zip}`;

      const subtotal = getCartSubtotal();
      const tax = getCartTax(subtotal);
      const grandTotal = subtotal + tax;

      const now = new Date();
      const orderPayload = {
        action: 'createOrder',
        name: currentUser.name,
        email: currentUser.email,
        phone: phone,
        date: now.toLocaleDateString(),
        orderTimestamp: now.toLocaleString(),
        address: street,
        city: city,
        state: `${state} ${zip}`,
        orderId: orderId,
        orderedItems: cart.map(it => `${it.name} (x${it.qty}) - $${(Number(it.price) * it.qty).toFixed(2)}`).join(', '),
        items: cart.map(it => ({
          name: it.name,
          price: Number(it.price || 0),
          qty: parseInt(it.qty, 10) || 1,
          total: (Number(it.price || 0) * (parseInt(it.qty, 10) || 1)).toFixed(2)
        })),
        subTotal: `$${subtotal.toFixed(2)}`,
        tax: `$${tax.toFixed(2)}`,
        total: `$${grandTotal.toFixed(2)}`,
        paymentStatus: 'Pending',
        orderStatus: 'Received',
        orderType: isBusiness ? `Commercial (${bName})` : 'Residential'
      };

      // Send to Google Apps Script Orders Webhook
      const targetEndpoint = (typeof ORDERS_SCRIPT_URL !== 'undefined' && ORDERS_SCRIPT_URL) ? ORDERS_SCRIPT_URL : SCRIPT_URL;
      if (targetEndpoint && targetEndpoint.startsWith('https://')) {
        try {
          await fetch(targetEndpoint, {
            method: 'POST',
            mode: 'no-cors',
            headers: {
              'Content-Type': 'text/plain;charset=utf-8'
            },
            body: JSON.stringify(orderPayload)
          });
        } catch (err) {
          console.warn('Backend order dispatch note:', err);
        }
      }

      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = origBtnHtml;
      }

      document.getElementById('success-order-details').innerHTML = `
        Thank you, <strong>${currentUser.name}</strong>!<br>
        Your order <strong>#${orderId}</strong> for <strong>$${grandTotal.toFixed(2)}</strong> has been placed.<br><br>
        <span class="text-xs text-gray-600 block text-left bg-gray-50 p-3.5 rounded-xl border border-gray-100 space-y-1.5">
          <div class="flex items-center gap-1.5 text-emerald-700 font-bold mb-1">
            <i class="fa-solid fa-file-pdf"></i>
            <span>Invoice PDF generated & emailed to ${currentUser.email}</span>
          </div>
          <div><strong>Recipient:</strong> ${currentUser.email} (${phone})</div>
          ${isBusiness ? `<div><strong>Business:</strong> ${bName}</div>` : ''}
          <div><strong>Deliver to:</strong> ${fullAddress}</div>
          <div class="pt-2 mt-1 border-t border-gray-200 text-[11px] space-y-0.5">
            <div class="flex justify-between text-gray-500"><span>Subtotal:</span><span>$${subtotal.toFixed(2)}</span></div>
            <div class="flex justify-between text-gray-500"><span>Sales Tax (${getTaxRateDisplay()}):</span><span>$${tax.toFixed(2)}</span></div>
            <div class="flex justify-between font-bold text-gray-800 text-xs pt-1"><span>Total Paid:</span><span>$${grandTotal.toFixed(2)}</span></div>
          </div>
        </span>
      `;

      cart = [];
      saveCart();
      renderCart();
      document.getElementById('checkout-order-form').reset();
      document.getElementById('order-success-modal').classList.remove('hidden');
    }

    function closeOrderSuccessModal() {
      document.getElementById('order-success-modal').classList.add('hidden');
      navigate('home');
    }

    window.onload = init;