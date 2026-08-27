package com.spicemart.app

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Build
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.annotation.RequiresApi

class SpiceMartWebViewClient(
    private val context: Context,
    private val onPageLoadStarted: () -> Unit,
    private val onPageLoadFinished: (url: String?) -> Unit,
    private val onPageLoadError: (errorCode: Int, description: String?) -> Unit
) : WebViewClient() {

    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
        val url = request?.url?.toString() ?: return false
        return handleUrlRouting(view, url)
    }

    @Deprecated("Deprecated in Java")
    override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
        if (url == null) return false
        return handleUrlRouting(view, url)
    }

    private fun handleUrlRouting(view: WebView?, url: String): Boolean {
        // Handle common external schemes natively
        if (url.startsWith("tel:") || 
            url.startsWith("mailto:") || 
            url.startsWith("sms:") || 
            url.startsWith("geo:") || 
            url.startsWith("whatsapp:")) {
            try {
                val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
                context.startActivity(intent)
                return true
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        // Handle Google Auth / External OAuth redirect tabs if needed
        val uri = Uri.parse(url)
        val host = uri.host ?: ""

        // Keep SpiceMart and associated script domains in the WebView
        if (host.contains("naninice2000.github.io") || 
            host.contains("script.google.com") || 
            host.contains("script.googleusercontent.com") ||
            host.contains("accounts.google.com")) {
            return false // Load inside WebView
        }

        // For third-party external links, open in the device browser
        try {
            val intent = Intent(Intent.ACTION_VIEW, uri)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            context.startActivity(intent)
            return true
        } catch (e: Exception) {
            return false
        }
    }

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        onPageLoadStarted()
    }

    override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        onPageLoadFinished(url)
    }

    @RequiresApi(Build.VERSION_CODES.M)
    override fun onReceivedError(
        view: WebView?,
        request: WebResourceRequest?,
        error: WebResourceError?
    ) {
        super.onReceivedError(view, request, error)
        // Only trigger offline error if it's the main frame
        if (request?.isForMainFrame == true) {
            onPageLoadError(error?.errorCode ?: -1, error?.description?.toString())
        }
    }

    @Suppress("DEPRECATION")
    override fun onReceivedError(
        view: WebView?,
        errorCode: Int,
        description: String?,
        failingUrl: String?
    ) {
        super.onReceivedError(view, errorCode, description, failingUrl)
        onPageLoadError(errorCode, description)
    }
}
