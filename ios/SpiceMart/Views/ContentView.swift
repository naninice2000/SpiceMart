import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = WebViewModel()
    @StateObject private var networkMonitor = NetworkMonitor.shared
    
    var body: some View {
        ZStack(alignment: .top) {
            // Main Web Content or Offline State
            if networkMonitor.isConnected && !viewModel.hasFailedInitialLoad {
                WebViewContainer(url: AppConfig.storeURL, viewModel: viewModel)
                    .edgesIgnoringSafeArea(.bottom)
            } else {
                OfflineView {
                    if networkMonitor.isConnected {
                        viewModel.hasFailedInitialLoad = false
                        viewModel.reload()
                    }
                }
            }
            
            // Top Linear Progress Indicator
            if viewModel.isLoading && viewModel.estimatedProgress < 1.0 {
                ProgressView(value: viewModel.estimatedProgress, total: 1.0)
                    .progressViewStyle(LinearProgressViewStyle(tint: AppConfig.emerald600))
                    .frame(height: 3)
                    .transition(.opacity)
            }
        }
        .background(AppConfig.emerald600.edgesIgnoringSafeArea(.top))
    }
}
