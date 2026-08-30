/**
 * ==========================================================================
 * SpiceMart - Application Configuration File
 * ==========================================================================
 * 
 * Edit these settings without modifying core application code (assets/js/app.js).
 * Any changes made here take effect immediately upon page reload.
 */

window.CONFIG = {
  // ==========================================
  // GOOGLE APPS SCRIPT WEBHOOK ENDPOINTS
  // ==========================================
  
  // 1. Products Catalog & Live Search Endpoint
  SCRIPT_URL: 'https://script.google.com/macros/s/AKfycbzneULs0vFdvv1kMutfck8_i03B6lJ8EZdG9_ICIfFsyKNbO4kkSaZKfx9azOtTjKR6/exec',

  // 2. Orders Processing, Google Sheet Storage, PDF Invoice & Email Dispatch Endpoint
  ORDERS_SCRIPT_URL: 'https://script.google.com/macros/s/AKfycbxshnK3l1cRswHFR65M75Y6wNE_hzMj9dSPoLRdPJVd99M85iKSewA_QTN_4eV-1n4jrA/exec',

  // 3. Customer Management (Profiles, Addresses & Auto-population) Endpoint
  CUSTOMERS_SCRIPT_URL: 'https://script.google.com/macros/s/AKfycbyjiEWsmjPNMkn6XbMDZ76tsfBQN2L_gwZJjUwUqqEObwPvtoF3tmAlNV7RhTRWMMoIbw/exec',

  // ==========================================
  // STORE BRANDING & DETAILS
  // ==========================================
  STORE_NAME: 'SpiceMart',
  STORE_TAGLINE: 'Indian & Mexican Groceries',

  // ==========================================
  // THIRD-PARTY INTEGRATIONS & API KEYS
  // ==========================================
  
  // Google Sign-In OAuth 2.0 Client ID
  GOOGLE_CLIENT_ID: '460683061183-9el98nqfh0djo2qc215lcmb140ini306.apps.googleusercontent.com',

  // Google Maps Platform API Key (for Places Autocomplete & Address Geocoding)
  GOOGLE_MAPS_API_KEY: 'AIzaSyDOq7G_nS3SfFjTHVdI_lrYTK1Jofzf4nE',

  // ==========================================
  // STORE POLICIES & APP PREFERENCES
  // ==========================================
  
  // Sales Tax Rate (e.g., 0.0825 = 8.25%)
  TAX_RATE: 0.0825,

  // LocalStorage Cache Key for Product Inventory
  CACHE_KEY: 'spicemart_products_v6'
};
