import Foundation

func customAdd (_ lhs: Int, _ rhs: Int, using function: (Int, Int) -> Int) -> Int
{
    function(lhs, rhs)
}

customAdd(20, 30)
        {
            (lhs: Int, rhs: Int) -> Int in
            lhs + rhs
        }

customAdd(20, 40)
        {
            (lhs, rhs) in
            lhs + rhs
        }

customAdd(20, 40) { $0 + $1 }

let myArray = [10, 20, 30, 40]

myArray.sorted(by: <)
