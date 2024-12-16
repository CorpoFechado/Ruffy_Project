import csv
from datetime import datetime

NOTES_FILE = "notes.csv"

def load_notes():
    """Load notes from the CSV file."""
    notes = {}
    try:
        with open(NOTES_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes[row["title"]] = {
                    "content": row["content"],
                    "date": row["date"]
                }
    except FileNotFoundError:
        pass
    return notes

def save_notes(notes):
    """Save notes to the CSV file."""
    with open(NOTES_FILE, "w", newline="") as f:
        fieldnames = ["title", "content", "date"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for title, note in notes.items():
            writer.writerow({"title": title, "content": note["content"], "date": note["date"]})

def list_notes(notes, show_index=True):
    """List all notes with their titles and creation dates."""
    if not notes:
        print("\nNo notes found.")
        return []
    
    print("\nYour Notes:")
    indexed_titles = []
    for idx, (title, note) in enumerate(notes.items(), start=1):
        if show_index:
            print(f"{idx}. {title} (Date: {note['date']})")
        else:
            print(f"{title} (Date: {note['date']})")
        indexed_titles.append(title)
    print()
    return indexed_titles

def choose_note(notes):
    """Allow the user to select a note from the list."""
    indexed_titles = list_notes(notes)
    if not indexed_titles:
        return None
    try:
        choice = int(input("Enter the number of the note: "))
        if 1 <= choice <= len(indexed_titles):
            return indexed_titles[choice - 1]
        else:
            print("Invalid choice. Please try again.\n")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.\n")
        return None

def add_note(notes):
    """Add a new note."""
    title = input("Enter the title of the note: ").strip()
    if title in notes:
        print("A note with this title already exists. Please choose a different title.")
        return
    
    print("Enter the content of the note. Press Enter on a blank line to finish.")
    content_lines = []
    while True:
        line = input(" > ")
        if not line.strip():
            break
        content_lines.append(line)
    
    content = "\n".join(content_lines)
    notes[title] = {
        "content": content,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_notes(notes)
    print(f"Note '{title}' added successfully.\n")

def view_note(notes):
    """View a specific note."""
    title = choose_note(notes)
    if not title:
        return
    note = notes[title]
    print(f"\nTitle: {title}")
    print(f"Date: {note['date']}")
    print(f"Content:\n{note['content']}\n")

def edit_note(notes):
    """Edit an existing note directly in the terminal."""
    title = choose_note(notes)
    if not title:
        return
    
    note = notes[title]
    print("\nCurrent Content:")
    print(note["content"])
    print("\nEdit your note. Press Enter on a blank line to finish editing.")

    # Allow user to enter new content line by line
    new_content = []
    while True:
        line = input("> ")
        if not line.strip():  # Blank line indicates the end of editing
            break
        new_content.append(line)
    
    # Join the new content lines
    new_content = "\n".join(new_content)

    # Ask user to save the changes or discard them
    print("\nEdited Content:")
    print(new_content)
    confirm = input(f"Do you want to save the changes to '{title}'? (y/n): ").lower()
    if confirm == "y":
        note["content"] = new_content.strip()
        note["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_notes(notes)
        print(f"Note '{title}' updated successfully.\n")
    else:
        print("Changes discarded.\n")

def delete_note(notes):
    """Delete a note."""
    title = choose_note(notes)
    if not title:
        return
    confirm = input(f"Are you sure you want to delete the note '{title}'? (y/n): ").lower()
    if confirm == 'y':
        del notes[title]
        save_notes(notes)
        print(f"Note '{title}' deleted successfully.\n")
    else:
        print("Deletion cancelled.\n")

def search_notes(notes):
    """Search for notes by title or content."""
    keyword = input("Enter a keyword to search: ").lower()
    results = {title: note for title, note in notes.items() if keyword in title.lower() or keyword in note["content"].lower()}
    if results:
        print("\nSearch Results:")
        for title, note in results.items():
            print(f"{title} (Date: {note['date']})")
    else:
        print("No notes found matching the keyword.\n")

def main():
    notes = load_notes()
    while True:
        print("=== Note-Taking App ===")
        print("1. List Notes")
        print("2. Add Note")
        print("3. View Note")
        print("4. Edit Note")
        print("5. Delete Note")
        print("6. Search Notes")
        print("7. Exit")
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            list_notes(notes, show_index=False)
        elif choice == "2":
            add_note(notes)
        elif choice == "3":
            view_note(notes)
        elif choice == "4":
            edit_note(notes)
        elif choice == "5":
            delete_note(notes)
        elif choice == "6":
            search_notes(notes)
        elif choice == "7":
            print("Exiting the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
