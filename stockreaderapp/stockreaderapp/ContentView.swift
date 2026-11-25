//
//  ContentView.swift
//  stockreaderapp
//
//  Created by Justin Forbes on 10/6/26.
//

// So this app has a single purpose so I think it only needs one to max 3 views?
import SwiftUI
import AVFoundation

struct ContentView: View {
    
    // Value that triggers jump to camera screen
    @State private var isCameraView = false
    
    var body: some View {
        NavigationStack{
            VStack(spacing: 12){
                Image(systemName: "camera")
                    .font(.system(size: 48))
                    .foregroundStyle(.red)
                Text("Welcome!")
                    .font(.largeTitle.bold())
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .padding()
            .safeAreaInset(edge: .bottom){
                Button("Start Camera"){
                    isCameraView = true
                }
                .navigationDestination(isPresented: $isCameraView) {
                    CameraView()
                }
                .tint(.gray)
                .buttonStyle(.glassProminent)
                .controlSize(.large)
                .padding()
            }
        }
    }
}

struct CameraView: View {
    @StateObject private var camera = CameraManager()

    var body: some View {
        ZStack {
            switch camera.authStatus {
            case .authorized:
                CameraPreview(session: camera.session)
                    .ignoresSafeArea()
            case .denied, .restricted:
                VStack {
                    Text("Camera access is disabled")
                    Button("Allow Camera Access") {
                        if let url = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(url)
                        }
                    }
                }
            default:
                ProgressView()
            }
        }
        .safeAreaInset(edge: .top) {
            if let company = camera.detectedCompany {
                Text(company)
                    .font(.headline)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial, in: Capsule())
            }
        }
        .onAppear { camera.checkAuth() }
    }
}

#Preview {
    ContentView()
}
