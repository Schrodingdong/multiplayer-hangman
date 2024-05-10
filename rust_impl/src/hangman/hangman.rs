use std::io;

const FORBIDDEN_CHARS: [char; 1]= [' '];

fn revealCharInWord(c: char, w: &String, revealedWord: &String)-> (String, bool) {
    let mut ogCharIter = w.chars();
    let mut newRevealedWord = String::new();
    let mut didReveal = false;
    for i in 0..revealedWord.len() {
        let ogWordChar = ogCharIter.next().unwrap();
        let currentRevealedWordChar = revealedWord.chars().nth(i).unwrap();
        if currentRevealedWordChar != '_' {
            newRevealedWord.push(currentRevealedWordChar);
            continue;
        }else {
            if c == ogWordChar {
                newRevealedWord.push(c);
                didReveal = true;
            } else {
                newRevealedWord.push('_');
            }
        }
        
    }
    return (newRevealedWord, didReveal);
}
fn initRevealedWord(w: &String)-> String {
    let mut revealedWord = String::new();
    for i in 0..w.len() {
        if w.chars().nth(i).unwrap() == ' ' {
            revealedWord.push(' ');
        } else {
            revealedWord.push('_');
        }
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

fn checkWordEquality(w1: &String, w2: &String)-> bool {
    if w1.len() != w2.len(){
        return false;
    }
    for i in 0..w1.len(){
        let c1 = w1.chars().nth(i).unwrap();
        let c2 = w2.chars().nth(i).unwrap();
        if c1 != c2 {
            return false
        }
    }
    return true;
}

fn main() {
    // VARIABLES =========================================
    const maxTries: u8 = 6;
    let mut tries = 0;
    let mut wordToGuess = String::new();
    let mut revealedWord: String;
    let mut revealedChars: Vec<char> = vec![];
    // ===================================================

    // get word to guess
    println!("Give word to guess : ");
    io::stdin()
        .read_line(&mut wordToGuess)
        .expect("Failed to read the word");
    wordToGuess.pop();
    wordToGuess.pop();
    wordToGuess = "hanae zwina bzaf".to_string();
    revealedWord= initRevealedWord(&wordToGuess);
    println!("word : {}", formatRevealedWord(&revealedWord));


    while tries < maxTries && !revealedWord.eq(&wordToGuess){
        println!("--------------------------------------");
        // take input
        println!("What is your guess ? (guesses remaining : {})", maxTries-tries);
        let mut guess = String::new();
        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");
        let guessedChar: char = guess.chars().next().unwrap();
        // make sure its not a forbidden character
        let mut isForbidden = false;
        for forbiddenChar in FORBIDDEN_CHARS {
            if guessedChar == forbiddenChar {
                println!(">>> Forbidden character : {}", guessedChar);
                isForbidden = true;
            }
        }
        if isForbidden {
            continue;
        }

        // make sure its not already revealed
        let mut isAlreadyRevealed = false;
        for revealedChar in &revealedChars {
            if guessedChar == *revealedChar {
                println!(">>> Character already guessed : {}", guessedChar);
                isAlreadyRevealed = true;
            }
        }
        if isAlreadyRevealed {
            continue;
        }

        // check
        let charIter = wordToGuess.chars();
        let didReveal: bool;
        (revealedWord, didReveal) = revealCharInWord(guessedChar, &wordToGuess, &revealedWord);
        println!("Revealed word : {}", formatRevealedWord(&revealedWord));
        if !didReveal {
            tries += 1;
        } else {
            revealedChars.push(guessedChar);
        }
    }

    // win screen :
        println!("\n\n========================================================");
    if revealedWord.eq(&wordToGuess) {
        println!("You won !");
    } else {
        println!("You lost!");
    }
    println!("========================================================");

}