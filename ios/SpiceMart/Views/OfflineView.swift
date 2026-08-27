import SwiftUI

struct OfflineView: View {
    let onRetry: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Spacer()
            
            ZStack {
                Circle()
                    .fill(Color(uiColor: .systemGray6))
                    .frame(width: 100, height: 100)
                
                Image(systemName: "wifi.slash")
                    .font(.system(size: 44, weight: .semibold))
                    .foregroundColor(.secondary)
            }
            
            VStack(spacing: 8) {
                Text("No Internet Connection")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.primary)
                
                Text("Please check your Wi-Fi or cellular network connection and try again.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
            }
            
            Button(action: onRetry) {
                HStack(spacing: 8) {
                    Image(systemName: "arrow.clockwise")
                        .font(.headline)
                    Text("Retry Connection")
                        .font(.headline)
                }
                .foregroundColor(.white)
                .padding(.horizontal, 28)
                .padding(.vertical, 14)
                .background(AppConfig.emerald600)
                .cornerRadius(14)
                .shadow(color: AppConfig.emerald600.opacity(0.3), radius: 8, x: 0, y: 4)
            }
            .padding(.top, 12)
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(uiColor: .systemBackground))
    }
}
