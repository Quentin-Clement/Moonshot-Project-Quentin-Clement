//        ScrollViewReader { proxy in
//            ScrollView(.vertical, showsIndicators: false) {
//
//            }
//        }
//        .navigationTitle("My App")
//        .toolbarBackground(.visible, for: .navigationBar)
//        .toolbarBackground(Color("Purple"), for: .navigationBar)
//        .toolbarColorScheme(.dark, for: .navigationBar)

import SwiftUI

struct Home: View {
    @Namespace var namespace
    @State var show = false
    
    var body: some View {
        ZStack {
            if !show {
                ZStack {
                    Color.mint
                    VStack {
                        Image("logo")
                            .resizable()
                            .frame(width: 150, height: 150)
                        Text("My App")
                            .font(.system(size: 70))
                            .fontWeight(.bold)
                            .foregroundColor(Color.white)
                    }
                }
                .ignoresSafeArea()
            } else {
//                NavigationStack
//                {
//                    ScrollViewReader { proxy in
//                        ScrollView(.vertical, showsIndicators: false) {
//                            
//                        }
//                    }
//                    .navigationTitle("My App")
//                    .toolbarBackground(.visible, for: .navigationBar)
//                    .toolbarBackground(Color.mint, for: .navigationBar)
//                    .toolbarColorScheme(.dark, for: .navigationBar)
//
//                }
                
                NavigationStack {
                        List {
                            Text("Hello, SwiftUI!")
                        }
                        .navigationTitle("Navigation Title")
                        .toolbarBackground(
                            // 1
                            Color.mint,
                            // 2
                            for: .navigationBar)
                        .toolbarBackground(.visible, for: .navigationBar)
                    }
            }
        }
        .onTapGesture {
            withAnimation {
                show.toggle()
            }
        }
    }
}

#Preview {
    ContentView()
}
