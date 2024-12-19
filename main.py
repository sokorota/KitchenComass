import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore

class RecipeManagerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rezept-Manager")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        self.createDatabase()

    def initUI(self):
        # Main Layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Recipe List
        self.recipe_list = QtWidgets.QListWidget()
        self.recipe_list.itemClicked.connect(self.loadRecipe)
        self.layout.addWidget(self.recipe_list)

        # Buttons
        self.button_layout = QtWidgets.QHBoxLayout()

        self.add_button = QtWidgets.QPushButton("Rezept hinzufügen")
        self.add_button.clicked.connect(self.addRecipe)
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QtWidgets.QPushButton("Rezept löschen")
        self.delete_button.clicked.connect(self.deleteRecipe)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

        # Recipe Details
        self.recipe_details = QtWidgets.QTextEdit()
        self.recipe_details.setReadOnly(True)
        self.layout.addWidget(self.recipe_details)

    def createDatabase(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect("recipes.db")
        self.cursor = self.conn.cursor()

        # Create table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT,
            instructions TEXT
        )
        """)
        self.conn.commit()
        self.loadRecipes()

    def loadRecipes(self):
        self.recipe_list.clear()
        self.cursor.execute("SELECT id, title FROM recipes")
        recipes = self.cursor.fetchall()
        for recipe_id, title in recipes:
            item = QtWidgets.QListWidgetItem(title)
            item.setData(QtCore.Qt.UserRole, recipe_id)
            self.recipe_list.addItem(item)

    def loadRecipe(self, item):
        recipe_id = item.data(QtCore.Qt.UserRole)
        self.cursor.execute("SELECT ingredients, instructions FROM recipes WHERE id = ?", (recipe_id,))
        recipe = self.cursor.fetchone()
        if recipe:
            ingredients, instructions = recipe
            self.recipe_details.setText(f"**Zutaten:**\n{ingredients}\n\n**Zubereitung:**\n{instructions}")

    def addRecipe(self):
        dialog = AddRecipeDialog(self)
        if dialog.exec_():
            title, ingredients, instructions = dialog.getRecipeData()
            self.cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                                (title, ingredients, instructions))
            self.conn.commit()
            self.loadRecipes()

    def deleteRecipe(self):
        current_item = self.recipe_list.currentItem()
        if current_item:
            recipe_id = current_item.data(QtCore.Qt.UserRole)
            self.cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            self.conn.commit()
            self.loadRecipes()
            self.recipe_details.clear()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

class AddRecipeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rezept hinzufügen")
        self.setFixedSize(400, 300)
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.title_input = QtWidgets.QLineEdit()
        self.title_input.setPlaceholderText("Rezeptname")
        layout.addWidget(self.title_input)

        self.ingredients_input = QtWidgets.QTextEdit()
        self.ingredients_input.setPlaceholderText("Zutaten (eine pro Zeile)")
        layout.addWidget(self.ingredients_input)

        self.instructions_input = QtWidgets.QTextEdit()
        self.instructions_input.setPlaceholderText("Zubereitung")
        layout.addWidget(self.instructions_input)

        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def getRecipeData(self):
        return (self.title_input.text(), self.ingredients_input.toPlainText(), self.instructions_input.toPlainText())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RecipeManagerApp()
    window.show()
    sys.exit(app.exec_())
