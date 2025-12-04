import json
from datetime import datetime
import os

# ---------------- File Storage Class ----------------
class FileStorage:
    def __init__(self, data_file="library_data.json"):
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self):
        """Load data from JSON file or create default structure"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default data structure
        return {
            "books": [],
            "library_cards": [],
            "borrowers": [],
            "next_book_id": 1,
            "next_card_no": 1,
            "next_borrower_id": 1
        }

    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def get_next_id(self, key):
        """Get next available ID and increment"""
        next_id = self.data[key]
        self.data[key] += 1
        return next_id

# ---------------- Library System ----------------
class LibrarySystem:
    def __init__(self, storage: FileStorage):
        self.storage = storage

    # --------- Book Operations ---------
    def add_book(self):
        try:
            print("\n--- ADD NEW BOOK ---")
            title = input("Enter Book Title: ").strip()
            author = input("Enter Author Name: ").strip()
            genre = input("Enter Genre: ").strip()
            copies = int(input("Enter Number of Copies: "))
            
            book_id = self.storage.get_next_id("next_book_id")
            
            new_book = {
                "book_id": book_id,
                "title": title,
                "author": author,
                "genre": genre,
                "copies": copies
            }
            
            self.storage.data["books"].append(new_book)
            self.storage.save_data()
            
            print("\n✅ Book added successfully!")
            print(f"Book ID: {book_id}")
            
        except ValueError:
            print("❌ Invalid input. Copies must be a number.")
        except Exception as e:
            print(f"❌ Error: {e}")

    def list_books(self):
        books = self.storage.data["books"]
        if not books:
            print("\n❌ No books found in the library.")
            return
        
        print("\n--- ALL BOOKS ---")
        print("ID  | Title                | Author           | Genre        | Copies")
        print("-" * 70)
        
        for book in books:
            print(f"{book['book_id']:3} | {book['title'][:20]:20} | {book['author'][:15]:15} | {book['genre'][:12]:12} | {book['copies']:6}")

    def find_book(self, book_id):
        """Find book by ID"""
        for book in self.storage.data["books"]:
            if book["book_id"] == book_id:
                return book
        return None

    def update_book_copies(self, book_id, change):
        """Update book copies (positive to add, negative to subtract)"""
        book = self.find_book(book_id)
        if book:
            book["copies"] += change
            if book["copies"] < 0:
                book["copies"] = 0
            self.storage.save_data()
            return True
        return False

    # --------- Library Card Operations ---------
    def issue_card(self):
        try:
            print("\n--- ISSUE LIBRARY CARD ---")
            name = input("Enter Reader's Name: ").strip()
            branch = input("Enter Branch Address: ").strip()
            subscription = int(input("Subscription (months): "))
            
            card_no = self.storage.get_next_id("next_card_no")
            
            new_card = {
                "card_no": card_no,
                "name": name,
                "branch": branch,
                "subscription": subscription,
                "issue_date": datetime.today().strftime('%Y-%m-%d')
            }
            
            self.storage.data["library_cards"].append(new_card)
            self.storage.save_data()
            
            print(f"\n✅ Library Card issued successfully!")
            print(f"Card Number: {card_no}")
            
        except ValueError:
            print("❌ Invalid input. Subscription must be a number.")

    def find_card(self, card_no):
        """Find library card by number"""
        for card in self.storage.data["library_cards"]:
            if card["card_no"] == card_no:
                return card
        return None

    # --------- Borrower / Issue Book ---------
    def issue_book(self):
        try:
            print("\n--- ISSUE BOOK ---")
            card_no = int(input("Card Number: "))
            
            # Check if card exists
            card = self.find_card(card_no)
            if not card:
                print("❌ Library card not found. Please issue a card first.")
                return
            
            name = input("Borrower's Name: ").strip()
            address = input("Address: ").strip()
            phone = input("Phone: ").strip()
            book_id = int(input("Book ID: "))
            
            # Check book availability
            book = self.find_book(book_id)
            if not book:
                print("❌ Book not found.")
                return
            
            if book["copies"] <= 0:
                print("❌ No copies available.")
                return
            
            # Create borrower record
            borrower_id = self.storage.get_next_id("next_borrower_id")
            issued_date = datetime.today().strftime('%Y-%m-%d')
            
            # Calculate return date (14 days from issue)
            return_date_obj = datetime.today().replace(day=datetime.today().day + 14)
            return_date = return_date_obj.strftime('%Y-%m-%d')
            
            new_borrower = {
                "borrower_id": borrower_id,
                "card_no": card_no,
                "name": name,
                "address": address,
                "phone": phone,
                "book_id": book_id,
                "book_title": book["title"],
                "issued_date": issued_date,
                "return_date": return_date
            }
            
            self.storage.data["borrowers"].append(new_borrower)
            
            # Update book copies
            self.update_book_copies(book_id, -1)
            self.storage.save_data()
            
            print(f"\n✅ Book issued successfully!")
            print(f"Borrower ID: {borrower_id}")
            print(f"Book: {book['title']}")
            print(f"Return Date: {return_date}")
            
        except ValueError:
            print("❌ Invalid input. Card Number and Book ID must be numbers.")

    # --------- Return Book ---------
    def return_book(self):
        try:
            print("\n--- RETURN BOOK ---")
            borrower_id = int(input("Enter Borrower ID to return book: "))
            
            # Find borrower
            borrower = None
            for br in self.storage.data["borrowers"]:
                if br["borrower_id"] == borrower_id:
                    borrower = br
                    break
            
            if not borrower:
                print("❌ Borrower record not found.")
                return
            
            # Update book copies
            self.update_book_copies(borrower["book_id"], 1)
            
            # Remove borrower record
            self.storage.data["borrowers"] = [
                br for br in self.storage.data["borrowers"] 
                if br["borrower_id"] != borrower_id
            ]
            
            self.storage.save_data()
            
            print("\n✅ Book returned successfully!")
            print(f"Book: {borrower['book_title']}")
            
        except ValueError:
            print("❌ Invalid input. Borrower ID must be a number.")

    # --------- View Borrower Details ---------
    def list_borrowers(self):
        borrowers = self.storage.data["borrowers"]
        if not borrowers:
            print("\n❌ No active borrowers found.")
            return
        
        print("\n--- ACTIVE BORROWERS ---")
        print("ID   | Name                | Phone       | Book Title          | Issued Date | Return Date")
        print("-" * 90)
        
        for borrower in borrowers:
            print(f"{borrower['borrower_id']:4} | {borrower['name'][:18]:18} | {borrower['phone'][:11]:11} | {borrower['book_title'][:19]:19} | {borrower['issued_date']} | {borrower['return_date']}")

    # --------- Search Books ---------
    def search_books(self):
        print("\n--- SEARCH BOOKS ---")
        keyword = input("Enter title or author to search: ").strip().lower()
        
        results = []
        for book in self.storage.data["books"]:
            if (keyword in book["title"].lower() or 
                keyword in book["author"].lower() or
                keyword in book["genre"].lower()):
                results.append(book)
        
        if not results:
            print("❌ No books found matching your search.")
            return
        
        print(f"\n📚 Found {len(results)} book(s):")
        for book in results:
            status = "Available" if book["copies"] > 0 else "Not Available"
            print(f"ID: {book['book_id']} | {book['title']} by {book['author']} | {status}")

    # --------- Library Statistics ---------
    def show_statistics(self):
        books = self.storage.data["books"]
        borrowers = self.storage.data["borrowers"]
        cards = self.storage.data["library_cards"]
        
        total_books = len(books)
        total_copies = sum(book["copies"] for book in books)
        available_books = sum(1 for book in books if book["copies"] > 0)
        active_borrowers = len(borrowers)
        total_members = len(cards)
        
        print("\n--- LIBRARY STATISTICS ---")
        print(f"📊 Total Books: {total_books}")
        print(f"📚 Total Copies: {total_copies}")
        print(f"✅ Available Books: {available_books}")
        print(f"👥 Active Borrowers: {active_borrowers}")
        print(f"🎫 Total Members: {total_members}")

# ---------------- Main Menu ----------------
def main():
    storage = FileStorage()
    system = LibrarySystem(storage)
    
    print("=" * 50)
    print("      📚 LIBRARY MANAGEMENT SYSTEM 📚")
    print("=" * 50)

    while True:
        print("\n--- MAIN MENU ---")
        print("1. Add Book")
        print("2. List All Books")
        print("3. Search Books")
        print("4. Issue Library Card")
        print("5. Issue Book")
        print("6. Return Book")
        print("7. View Active Borrowers")
        print("8. Library Statistics")
        print("9. Exit")
        print("-" * 20)

        try:
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                system.add_book()
            elif choice == "2":
                system.list_books()
            elif choice == "3":
                system.search_books()
            elif choice == "4":
                system.issue_card()
            elif choice == "5":
                system.issue_book()
            elif choice == "6":
                system.return_book()
            elif choice == "7":
                system.list_borrowers()
            elif choice == "8":
                system.show_statistics()
            elif choice == "9":
                print("\nThank you for using Library Management System! 👋")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-9.")
                
        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()