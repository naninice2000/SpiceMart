package com.spicemart.app

import android.annotation.SuppressLint
import android.content.res.Configuration
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebSettings
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.spicemart.app.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val appUrl by lazy { getString(R.string.app_url) }
    private var isPageLoadedSuccessfully = false

    override fun onCreate(savedInstanceState: Bundle?) {
        // 1. Install AndroidX Splash Screen before super.onCreate()
        installSplashScreen()
        
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // 2. Setup Status Bar and Navigation Bar colors
        setupSystemBars()

        // 3. Initialize WebView and Settings
        setupWebView()

        // 4. Setup Swipe-to-Refresh with Emerald Accent
        setupSwipeRefresh()

        // 5. Setup Hardware Back Navigation
        setupBackNavigation()

        // 6. Setup Offline Retry Handler
        setupOfflineRetry()

        // 7. Load Initial Store URL
        loadStoreUrl()
    }

    private fun setupSystemBars() {
        val windowInsetsController = WindowCompat.getInsetsController(window, window.decorView)
        // White text/icons on dark emerald status bar
        windowInsetsController.isAppearanceLightStatusBars = false
        
        // Match navigation bar with theme
        val isDarkMode = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES
        windowInsetsController.isAppearanceLightNavigationBars = !isDarkMode
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val webView = binding.webView
        val settings = webView.settings

        // Enable core web capabilities
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true

        // Viewport & Scaling
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.setSupportZoom(false)
        settings.builtInZoomControls = false
        settings.displayZoomControls = false

        // Cache & Performance
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        // Custom User Agent to ensure smooth Google OAuth & compatibility
        val defaultUserAgent = settings.userAgentString
        // Replace 'wv' tag if present to allow standard Google Identity Services
        val cleanUserAgent = defaultUserAgent.replace("; wv", "").replace("Version/4.0 ", "")
        settings.userAgentString = cleanUserAgent

        // Cookie Management
        val cookieManager = CookieManager.getInstance()
        cookieManager.setAcceptCookie(true)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true)
        }

        // Setup Clients
        webView.webViewClient = SpiceMartWebViewClient(
            context = this,
            onPageLoadStarted = {
                binding.progressBar.visibility = View.VISIBLE
            },
            onPageLoadFinished = { _ ->
                binding.progressBar.visibility = View.GONE
                binding.swipeRefreshLayout.isRefreshing = false
                isPageLoadedSuccessfully = true
                showContentView()
            },
            onPageLoadError = { _, _ ->
                binding.progressBar.visibility = View.GONE
                binding.swipeRefreshLayout.isRefreshing = false
                if (!NetworkUtils.isNetworkAvailable(this)) {
                    showOfflineView()
                }
            }
        )

        webView.webChromeClient = SpiceMartWebChromeClient(
            activity = this,
            onProgressUpdate = { progress ->
                if (progress in 1..99) {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.progressBar.setProgressCompat(progress, true)
                } else {
                    binding.progressBar.visibility = View.GONE
                }
            }
        )
    }

    private fun setupSwipeRefresh() {
        val swipeRefresh = binding.swipeRefreshLayout
        swipeRefresh.setColorSchemeResources(
            R.color.emerald_600,
            R.color.emerald_500,
            R.color.emerald_700
        )
        swipeRefresh.setProgressBackgroundColorSchemeResource(R.color.white)
        swipeRefresh.setOnRefreshListener {
            if (NetworkUtils.isNetworkAvailable(this)) {
                binding.webView.reload()
            } else {
                swipeRefresh.isRefreshing = false
                showOfflineView()
            }
        }
    }

    private fun setupBackNavigation() {
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (binding.offlineContainer.visibility == View.VISIBLE) {
                    finish()
                } else if (binding.webView.canGoBack()) {
                    binding.webView.goBack()
                } else {
                    finish()
                }
            }
        })
    }

    private fun setupOfflineRetry() {
        binding.btnRetry.setOnClickListener {
            loadStoreUrl()
        }
    }

    private fun loadStoreUrl() {
        if (NetworkUtils.isNetworkAvailable(this)) {
            showContentView()
            binding.webView.loadUrl(appUrl)
        } else {
            showOfflineView()
        }
    }

    private fun showContentView() {
        binding.swipeRefreshLayout.visibility = View.VISIBLE
        binding.offlineContainer.visibility = View.GONE
    }

    private fun showOfflineView() {
        binding.swipeRefreshLayout.visibility = View.GONE
        binding.offlineContainer.visibility = View.VISIBLE
    }

    override fun onResume() {
        super.onResume()
        binding.webView.onResume()
    }

    override fun onPause() {
        binding.webView.onPause()
        super.onPause()
    }

    override fun onDestroy() {
        binding.webView.destroy()
        super.onDestroy()
    }
}
