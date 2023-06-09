## Author: Pallavi Garg
pallavg1@uci.edu

## Prerequisites:
  - Python3.10 or higher
  - xclip for running on Linux machine

## Instructions:

Run following command to run the program:
    
   For main project - **SSA Based Optimized Compiler** :
   
        > python3.10 compiler.py testfiles/test1.smpl
    
   For project 1:
   
        > cd warmup_project1
        > python3.10 main_project1.py 1+2.
    
   For project 2:
   
        > cd warmup_project2
        > python3.10 main.py "computation var i <- 2*3; var ab <- 7; (((ab * i))); i - 5 - 1 ."
## Viewing Output
Output is viewed [here](http://www.webgraphviz.com/)

## Some Examples

1. If-Else program in SMPL language:
   ```
   main
    var a, b, c, d, e;
    {
        let a <- call InputNum();
        let b <- a;
        let c <- b;
        let d <- b + c;
        let e <- a + b;
        if a<0 then
            let d<-d+e;
            let a<-d
        else 
            let d<-e
        fi;
        call OutputNum(a)
    }.

   ```
   Output: 
   Here instruction number 2 is reused in 6.
   
   ![if-else](/docs/if-else.png)

2. While loop program in SMPL language:
   ```
   main
    var i, x, y, j;
    {
        let i <- call InputNum();
        let x <- 0;
        let y <- 0;
        let j <- i;
        while x < 10 do
            let x <- i + 1;
            let x <- x + 1;
            let y <- j + 1;
            let i <- i + 1;
        od;
        call OutputNum(i);
        call OutputNum(x);
        call OutputNum(j);
        call OutputNum(y)
    }.
   ```
   Output: 
   ![while-loop](/docs/while-loop.png)

3. Array in SMPL language:
   ```
   main 
    var i; 
    array[10] arr; 
    {
        while i < 10 do 
            if i < 10 then
                let arr[i] <- i + 1; 
                let i <-i + 1 
            fi;
        od; 
        call OutputNum(arr[i]);
        call OutputNum(arr[i])
    }.
   ```
   Output: 
   ![arrays](/docs/arrays.png)

4. Functions:
   ```
   main var a, b;
    function test(x, y);
    {       
        return x * call test(x - 1, y - 1);
    };
    {
        let a <- 5;
        let b <- 10;
        call OutputNum(call test(a, b));
    }.
   ```
   Output: 
   ![functions](/docs/functions.png)

- `*` marks the dead instructions and are shown here just for illustration.
- Kill statements are also shown for illustration.

# Assumptions

1. No two variables and functions will have same name.
