import os
# setting env flags before mediapipte c++ binaries are loaded to avoid broken Metal GPU initialization on macOS
os.environ["MEDIAPIPE_GPU"] = "0"

import sys



def display_menu():
    print("=" * 50)
    print("      HAND GESTURE CONTROLLED APPLICATION      ")
    print("=" * 50)
    print("  [1] Data Collector Mode") #Record gestures to CSV
    print("  [2] Training Mode") #Train ML classifier
    print("  [3] Game Mode") #Interactive graphics application
    print("  [4] Exit")
    print("=" * 50)

def main():
    while True:
        display_menu()
        choice = input("Select an option (1-4): ").strip()

        if choice == '1':
            from collect_data import run_collector
            run_collector()
        elif choice == '2':
            from train_model import train_and_find_best_model
            train_and_find_best_model()
        elif choice == '3':
            from game import run_game
            run_game()
        elif choice == '4':
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose 1, 2, 3, or 4.\n")

if __name__ == "__main__":
    main()