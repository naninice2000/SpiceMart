import Foundation
import WebKit

final class WebViewModel: ObservableObject {
    @Published var estimatedProgress: Double = 0.0
    @Published var isLoading: Bool = false
    @Published var canGoBack: Bool = false
    @Published var canGoForward: Bool = false
    @Published var shouldReload: Bool = false
    @Published var hasFailedInitialLoad: Bool = false
    
    var webView: WKWebView?
    
    func reload() {
        shouldReload = true
    }
    
    func goBack() {
        webView?.goBack()
    }
    
    func goForward() {
        webView?.goForward()
    }
}
