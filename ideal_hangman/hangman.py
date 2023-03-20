import random
from collections import defaultdict, Counter


def read_words_from_file(filename):
    with open(filename, 'r') as file:
        words = file.read().splitlines()

    print(len(words))
    
    # print("Completed importing words")
    return words


def group_words_by_length(words):
    length_groups = defaultdict(list)
    for word in words:
        length_groups[len(word)].append(word)
    
    # print(f"Completed grouping words ({len(length_groups)} groups)")
    return length_groups


def get_most_common_letters(words, current_guessing_progress):
    letter_counts = Counter()
    for word in words:
        letter_counts.update(list(word))

    # print(f"Most common letters: {letter_counts.most_common()}")
    most_common = [letter for letter, _ in letter_counts.most_common()]

    for c in current_guessing_progress:
        try:
            most_common.remove(c)
        except ValueError:
            pass


    # print(words)
    # print(letter_counts.most_common())
    # print(most_common)

    return most_common


def filter_words(words, current_guessing_progress: list, guessed_letters):
    filtered_words = []
    candidates = []
    non_matches = []
    for word in words:
        # skip words that don't match the letter order of your current guessing progress
        def check1():
            for guessed_letter_index, guessed_letter in enumerate(current_guessing_progress):
                # for a correct guess, if the word you're considering doesn't match that
                # example, guessed_letters = [?, ?, e], eliminate a word that is "_ _ t"
                if guessed_letter != word[guessed_letter_index] and guessed_letter != "?":
                    non_matches.append(word)
                    return True

                # eliminate words where you guessed a letter but a considered word has too many of that letter
                # example, guessed letters - [?, ?, e], eliminate a word that is "_ e e"
                if guessed_letter == "?":
                    if word[guessed_letter_index] in guessed_letters:
                        non_matches.append(word)
                        return True

            candidates.append(word)
        if check1():
            continue

        # # remaining possible words only contain letters that you haven't guessed wrong already
        # # skip words that have one of the letters you already guessed
        # def check2():
        #     for letter in guessed_letters:
        #         if letter in word:
        #             print(f"already guessed letter: {letter}")
        #             return True
        # if check2():
        #     continue

        filtered_words.append(word)

    # print(f"Candidates: {candidates}")
    # print(f"not matching guessed letters: {non_matches}")
    # print("word filtering: ", current_guessing_progress, filtered_words)
    return filtered_words


def count_guesses(target_word, words_by_length):
    word_length = len(target_word)
    current_guessing_progress = ["?"]*word_length
    # print(target_word, words_by_length[word_length])
    guessed_letters = set()
    num_guesses = 0

    possible_words = filter_words(words_by_length[len(target_word)],
                                  current_guessing_progress,
                                  guessed_letters)
    # print("possible_words", possible_words)
    most_common_letters = get_most_common_letters(possible_words, current_guessing_progress)
    # print("most_common_letters", most_common_letters)

    while "?" in current_guessing_progress:
        for letter in most_common_letters:
            # print(f"GUESS!: {letter}")
            num_guesses += 1
            if letter not in guessed_letters:
                guessed_letters.add(letter)

            if letter in target_word:
                for l_index, target_letter in enumerate(target_word):
                    if target_letter == letter:
                        current_guessing_progress[l_index] = letter

                possible_words = filter_words(words_by_length[word_length], current_guessing_progress,
                                              guessed_letters)
                # print("possible_words", possible_words)
                most_common_letters = get_most_common_letters(possible_words, current_guessing_progress)
                # print("most_common_letters", most_common_letters)
                break

    return num_guesses


def find_most_difficult_words(words_by_length):
    most_difficult_words = {}
    second_most_difficult_words = {}
    count = 0
    # print(words_by_length.items())
    # print(words_by_length[8])
    for word_length, words in sorted(list(words_by_length.items())):
        # print("\n\n\n")
        max_guesses = 0
        difficult_words = []
        second_most_difficult_list = []

        for word in words:
            # if len(word) != 4:
            #     continue
            guesses = count_guesses(word, words_by_length)
            if guesses > max_guesses:
                max_guesses = guesses
                second_most_difficult_list = difficult_words
                difficult_words = [word]
            elif guesses == max_guesses:
                difficult_words.append(word)
            elif guesses == max_guesses - 1:
                second_most_difficult_list.append(word)

            count += 1
            if count % 500 == 0:
                print(word, count)

        most_difficult_words[word_length] = (max_guesses, difficult_words)
        second_most_difficult_words[word_length] = (max_guesses - 1, second_most_difficult_list)

    return most_difficult_words, second_most_difficult_words


def main():
    filename = "30k.txt"
    words = read_words_from_file(filename)
    words_by_length = group_words_by_length(words)
    most_difficult_words, second_most_difficult_words = find_most_difficult_words(words_by_length)

    for word_length, (max_guesses, difficult_words) in most_difficult_words.items():
        # second_most_difficult_words_list = [i[1] for i in second_most_difficult_words[word_length]]
        second_most_difficult_words_list = second_most_difficult_words[word_length][1]
        print(f"Word length: {word_length} ({len(words_by_length[word_length])} total words), "
              f"... Most difficult ({max_guesses} guesses): {', '.join(difficult_words)}, "
              f"... Less difficult ({max_guesses-1} guesses): {', '.join(second_most_difficult_words_list)}")


if __name__ == "__main__":
    main()
