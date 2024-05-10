use warp::{filters::path::end, Filter};
use warp::ws;


#[tokio::main]
async fn main() {
    // define my paths here
    let hello_world = warp::path::end()
        .map(|| "Hello World from root !");
    let hi = warp::path("hi")
        .map(|| "Hello World from hi !");
    let hi = warp::path("lmao")
        .map(|| "Hello World from lmao!");

    // group the paths into routess
    let routes = hello_world.or(hi);


    println!("Start web-server");
    let addr = ([127,0,0,1], 8080);
    warp::serve(ws).run(addr).await;
}
