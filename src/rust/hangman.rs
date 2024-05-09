use std::io;

fn revealCharInWord(c: char, w: &String, revealedWord: &String)-> String {
    let mut ogCharIter = w.chars();
    let mut newRevealedWord = String::new();
    for i in 0..revealedWord.len() {
        let ogWordChar = ogCharIter.next().unwrap();
        let currentRevealedWordChar = revealedWord.chars().nth(i).unwrap();
        if currentRevealedWordChar != '_' {
            newRevealedWord.push(currentRevealedWordChar);
            continue;
        }else {
            if c == ogWordChar {
                newRevealedWord.push(c);
            } else {
                newRevealedWord.push('_');
            }
        }
        
    }
    return newRevealedWord;
}
fn initRevealedWord(w: &String)-> String {
    let mut revealedWord = String::new();
    for i in 0..w.len()-1 {
        revealedWord.push('_');
    }
    return revealedWord;
}
fn formatRevealedWord(revealedWord: &String)-> String {
    let mut formattedRevealedWord = String::new();
    for c in revealedWord.chars() {
        formattedRevealedWord.push(c);
        formattedRevealedWord.push(' ');
    }
    return formattedRevealedWord;
}

fn main() {
    // VARIABLES =========================================
    const maxTries: u8 = 6;
    let mut tries = 0;
    let mut wordToGuess = String::new();
    let mut revealedWord: String;
    // ===================================================

    // get word to guess
    println!("Give word to guess : ");
    io::stdin()
        .read_line(&mut wordToGuess)
        .expect("Failed to read the word");
    revealedWord= initRevealedWord(&wordToGuess);
    println!("word : {}", formatRevealedWord(&revealedWord));


    while tries < maxTries && !revealedWord.eq(&wordToGuess){
        // take input
        println!("What is your guess ? (guesses remaining : {})", maxTries-tries);
        let mut guess = String::new();
        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");
        let guessedChar = guess.chars().next().unwrap();
        // check
        let charIter = wordToGuess.chars();
        revealedWord = revealCharInWord(guessedChar, &wordToGuess, &revealedWord);
        println!("revealed word : {}", formatRevealedWord(&revealedWord));
        tries += 1;
    }

    if !revealedWord.eq(&wordToGuess){
        println!("lost");
    } else {
        println!("won");
    }
}