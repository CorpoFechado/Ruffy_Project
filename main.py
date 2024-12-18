import csv
from datetime import datetime
import os

NOTES_FILE = "notes.csv"

# Clear terminal screen function
def clear_screen():
    """Clear the terminal screen based on the OS."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Load notes
def load_notes():
    """Load notes from the CSV file."""
    notes = {}
    pinned_note = None  # Variable to store the pinned note title
    
    try:
        with open(NOTES_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes[row["title"]] = {
                    "content": row.get("content", ""),
                    "date": row.get("date", "N/A"),
                    "tags": row.get("tags", "N/A"),
                    "pinned": row.get("pinned", "False") == "True"  # Convert to Boolean
                }
                if notes[row["title"]]["pinned"]:
                    pinned_note = row["title"]  # Load the pinned note title
    except FileNotFoundError:
        pass
    
    return notes, pinned_note

# Save notes
def save_notes(notes, pinned_note):
    """Save notes to the CSV file."""
    with open(NOTES_FILE, "w", newline="") as f:
        fieldnames = ["title", "content", "date", "tags", "pinned"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for title, note in notes.items():
            writer.writerow({
                "title": title,
                "content": note["content"],
                "date": note["date"],
                "tags": note["tags"],
                "pinned": "True" if title == pinned_note else "False"  # Set the pinned status
            })

def list_notes(notes, sort_by=None):
    """
    List all notes with their titles and tags, sorted by the given method.
    - sort_by: "alphabetical" or "date"
    """
    if not notes:
        print("\nNo notes found.")
        return []

    sort_by = sort_by or load_sort_preference()  # Use saved preference if not specified
    sorted_notes = sorted(
        notes.items(),
        key=lambda item: item[0].lower() if sort_by == "alphabetical" else item[1]["date"],
        reverse=(sort_by == "date")
    )

    print(f"\nYour Notes (sorted by {sort_by}):")
    indexed_titles = []
    for idx, (title, note) in enumerate(sorted_notes, start=1):
        print(f"{idx}. {title} - Tags: {note['tags']}")
        indexed_titles.append(title)
    print()
    return indexed_titles

# View a note
def view_note(notes, title):
    """View the content of a selected note."""
    if title not in notes:
        print("Note not found.")
        return

    note = notes[title]
    print("\n--- Note Details ---")
    print(f"Title: {title}")
    print(f"Tags: {note['tags']}")
    print(f"Date: {note['date']}")
    print(f"Content:\n{note['content']}")
    print("---------------------\n")

# Choose a note
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

# Add a new note
def add_note(notes):
    """Add a new note with optional tags."""
    title = input("Enter the title of the note: ").strip()
    if title in notes:
        print("A note with this title already exists. Please choose a different title.")
        return

    # Ask for tags first
    tags = input("Enter tags for this note (comma-separated): ").strip()

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
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tags": tags if tags else "N/A",
        "pinned": False  # New note is not pinned by default
    }
    save_notes(notes, None)  # Save notes, no pinned note
    print(f"Note '{title}' added successfully.\n")

def edit_note(notes):
    """Edit an existing note, including its title, tags, and content."""
    title = choose_note(notes)
    if not title:
        return

    note = notes[title]
    print("\n--- Current Note Details ---")
    print(f"Title: {title}")
    print(f"Tags: {note['tags']}")
    print(f"Content:\n{note['content']}")
    print(f"Date Added: {note['date']}")
    print("----------------------------\n")

    # Ask for new title
    new_title = input("Enter a new title (leave blank to keep the current title): ").strip()

    # Check if the new title already exists (except the current note)
    if new_title and new_title != title and new_title in notes:
        print("A note with this title already exists. Please choose a different title.")
        return

    # Ask for new tags
    new_tags = input("Enter new tags (leave blank to keep current): ").strip()

    # Ask the user for new content
    print("\nEdit the content of the note. Press Enter on a blank line to keep the current content.")
    new_content_lines = []
    while True:
        line = input(" > ").strip()
        if not line:  # If the line is empty, stop and keep the current content
            break
        new_content_lines.append(line)

    # If no new content provided, keep the old content
    new_content = "\n".join(new_content_lines) if new_content_lines else None

    confirm = input(f"Do you want to save the changes to this note? (y/n): ").lower()
    if confirm == "y":
        # Update title, tags, and content (if changes were provided)
        final_title = new_title if new_title else title
        if final_title != title:  # If the title is changed
            notes[final_title] = notes.pop(title)  # Rename the key in the dictionary
        if new_tags:
            notes[final_title]["tags"] = new_tags
        if new_content is not None:
            notes[final_title]["content"] = new_content

        # Preserve the original date
        notes[final_title]["date"] = note["date"]

        save_notes(notes, None)  # Save notes, no pinned note
        print(f"Note '{final_title}' updated successfully.\n")
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
        save_notes(notes, pinned_note)
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

# View notes by tag
def view_notes_by_tag(notes):
    """View all notes related to a specific tag."""
    tags = set()
    for note in notes.values():
        note_tags = note["tags"].split(",")
        tags.update(tag.strip() for tag in note_tags)

    if not tags:
        print("\nNo tags found.")
        return

    print("\nAvailable Tags:")
    indexed_tags = list(tags)
    for idx, tag in enumerate(indexed_tags, start=1):
        print(f"{idx}. {tag}")
    
    try:
        choice = int(input("Enter the number of the tag you want to view: "))
        if 1 <= choice <= len(indexed_tags):
            selected_tag = indexed_tags[choice - 1]
            print(f"\nNotes with tag: {selected_tag}")
            
            related_notes = {title: note for title, note in notes.items()
                             if selected_tag in note["tags"].split(",")}
            
            if related_notes:
                indexed_titles = []
                for idx, (title, note) in enumerate(related_notes.items(), start=1):
                    print(f"{idx}. {title}")
                    indexed_titles.append(title)
                
                choice = input("Enter the number of the note to view: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(indexed_titles):
                    chosen_title = indexed_titles[int(choice) - 1]
                    view_note(related_notes, chosen_title)
                else:
                    print("Invalid note index.\n")
            else:
                print("No notes found for this tag.")
        else:
            print("Invalid choice. Please try again.\n")
    except ValueError:
        print("Invalid input. Please enter a number.\n")

# Pin a note
def pin_note(notes):
    """Pin a note to the pinned notes list."""
    global pinned_note
    indexed_titles = list_notes(notes)
    if not indexed_titles:
        return

    try:
        choice = int(input("Enter the number of the note you want to pin: "))
        if 1 <= choice <= len(indexed_titles):
            title = indexed_titles[choice - 1]
            if pinned_note == title:
                print(f"Note '{title}' is already pinned.\n")
            else:
                pinned_note = title
                save_notes(notes, pinned_note)  # Save the pinned note to the CSV file
                print(f"Note '{title}' has been pinned.\n")
        else:
            print("Invalid choice. Please try again.\n")
    except ValueError:
        print("Invalid input. Please enter a number.\n")

# View pinned note (called directly to view the pinned note)
def view_pinned_note(notes):
    """View the pinned note."""
    global pinned_note
    if pinned_note:
        print(f"\n--- Viewing Pinned Note: {pinned_note} ---")
        view_note(notes, pinned_note)
    else:
        print("No note is currently pinned.\n")

# Remove pinned note
def remove_pinned_note(notes):
    """Remove the pinned note."""
    global pinned_note
    if pinned_note:
        print(f"Note '{pinned_note}' has been unpinned.")
        pinned_note = None  # Set pinned_note to None to unpin it
        save_notes(notes, pinned_note)  # Save the state with no pinned note
    else:
        print("No note is currently pinned.\n")

SORT_PREF_FILE = "sort_pref.txt"  # File to save user's sort preference

# Load sort preference
def load_sort_preference():
    """Load the user's sort preference from a file."""
    if os.path.exists(SORT_PREF_FILE):
        with open(SORT_PREF_FILE, "r") as f:
            return f.read().strip()
    return "alphabetical"  # Default sort preference

# Save sort preference
def save_sort_preference(sort_preference):
    """Save the user's sort preference to a file."""
    with open(SORT_PREF_FILE, "w") as f:
        f.write(sort_preference)



# Choose sort preference
def choose_sort_preference():
    """Prompt the user to select a sort preference and save it."""
    print("\nChoose a sort preference:")
    print("1. Alphabetical")
    print("2. By Date")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        save_sort_preference("alphabetical")
        print("Sort preference set to alphabetical.\n")
    elif choice == "2":
        save_sort_preference("date")
        print("Sort preference set to by date.\n")
    else:
        print("Invalid choice. Keeping the current sort preference.\n")

def main():
    global pinned_note
    notes, pinned_note = load_notes()  # Load notes and pinned note at startup

    while True:
        clear_screen()  # Clear the terminal screen each time the menu is displayed
        print("=== NOTEFFY ===")

        # Display pinned note below NOTEFFY title if there is one
        if pinned_note:
            print(f"\n--- Pinned Note: {pinned_note} ---\n")

        # Display choices
        print("1. List Notes")
        print("2. Add Note")
        print("3. View Note")
        print("4. Edit Note")
        print("5. Delete Note")
        print("6. Search Notes")
        print("7. View Notes by Tag")
        print("8. Pin Note")
        print("9. View Pinned Note")
        print("10. Remove Pinned Note")
        print("11. Choose Sort Preference")  # New option to choose and save sort preference
        print("12. Exit")

        # Get user choice
        choice = input("Choose an option: ").strip()

        if choice == "1":
            sort_by = load_sort_preference()  # Use the saved sort preference
            list_notes(notes, sort_by)
            input("Press any key to return to the main menu...")
        elif choice == "2":
            add_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "3":
            title = choose_note(notes)
            if title:
                view_note(notes, title)
            input("Press any key to return to the main menu...")
        elif choice == "4":
            edit_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "5":
            delete_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "6":
            search_notes(notes)
            input("Press any key to return to the main menu...")
        elif choice == "7":
            view_notes_by_tag(notes)
            input("Press any key to return to the main menu...")
        elif choice == "8":
            pin_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "9":
            view_pinned_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "10":
            remove_pinned_note(notes)
            input("Press any key to return to the main menu...")
        elif choice == "11":  # New case for choosing sort preference
            choose_sort_preference()
            input("Press any key to return to the main menu...")
        elif choice == "12":
            print("Exiting Noteffy. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()