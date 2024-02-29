//
//  Home.swift
//  My Test App
//
//  Created by Quentin Clément on 23/02/2024.
//

import SwiftUI

struct LoadingPage: View {
    var body: some View {
        NavigationStack
        {
            ScrollViewReader { proxy in
                ScrollView(.vertical, showsIndicators: false) {
                    
                }
            }
            .navigationTitle("My App")
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbarBackground(Color("Purple"), for: .navigationBar)
            .toolbarColorScheme(.dark, for: .navigationBar)

        }
    }
}

#Preview {
    LoadingPage()
}
