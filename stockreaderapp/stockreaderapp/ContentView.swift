//
//  ContentView.swift
//  stockreaderapp
//
//  Created by Justin Forbes on 10/6/26.
//

// So this app has a single purpose so I think it only needs one to max 3 views?
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 12){
            Image(systemName: "sparkles")
                .font(.system(size: 48))
                .foregroundStyle(.tint)
            Text("Welcome!")
                .font(.largeTitle.bold())
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
        .safeAreaInset(edge: .bottom){
            Button{
                
            } label: {
                Text("Start Camera")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.glassProminent)
            .controlSize(.large)
            .padding()
        }
    }
}


#Preview {
    ContentView()
}

