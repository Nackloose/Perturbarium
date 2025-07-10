# src/licensee/keygen_ui.py

import sys
import os
import random
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt

# Add the parent directory (src) to sys.path to make the licensee package discoverable
# This assumes the script is run from the project root or a directory where src is a direct subdirectory
script_dir = os.path.dirname(__file__)
src_dir = os.path.join(script_dir, "..")
sys.path.insert(0, src_dir)

# Import our license generation function and crypto functions
from licensee.license_manager import generate_license_key
from licensee.crypto import (
    load_private_key_from_path,
    save_private_key_to_file,
    generate_rsa_key_pair,
    save_public_key_to_file,
)


class KeyGenWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.private_key = None  # To store the loaded private key
        self.private_key_path = ""  # To store the path to the private key file

        self.setWindowTitle("EP Studio License Key Generator")
        self.setGeometry(100, 100, 400, 450)  # Slightly increase window height

        # Center the window on the primary screen
        primary_screen = QApplication.primaryScreen()
        if primary_screen:
            screen_geometry = primary_screen.availableGeometry()
            window_geometry = self.geometry()
            x = (
                screen_geometry.x()
                + (screen_geometry.width() - window_geometry.width()) // 2
            )
            y = (
                screen_geometry.y()
                + (screen_geometry.height() - window_geometry.height()) // 2
            )
            self.move(x, y)

        self.layout = QVBoxLayout()

        # Input fields
        self.plan_input = self._add_input_row("License Plan (int):")
        self.duration_input = self._add_input_row("Duration (days):")
        self.group_input = self._add_input_row("Key Holder Group (int):")
        self.unique_id_input = self._add_input_row("Unique License ID (int):")
        self.version_lock_input = self._add_input_row(
            "Version Lock (int, 0 for none):", default_text="0"
        )

        # Swap param option
        swap_param_layout = QHBoxLayout()
        self.use_included_swap_param_checkbox = QCheckBox("Use Included Swap Param")
        self.use_included_swap_param_checkbox.setChecked(True)  # Default to included
        self.fixed_swap_param_label = QLabel("Fixed Swap Param (float):")
        self.fixed_swap_param_input = QLineEdit()
        self.fixed_swap_param_input.setEnabled(False)  # Disabled by default

        swap_param_layout.addWidget(self.use_included_swap_param_checkbox)
        swap_param_layout.addWidget(self.fixed_swap_param_label)
        swap_param_layout.addWidget(self.fixed_swap_param_input)
        self.layout.addLayout(swap_param_layout)

        # Connect checkbox signal to update fixed_swap_param_input state
        self.use_included_swap_param_checkbox.stateChanged.connect(
            self._update_swap_param_input_state
        )

        # Private key selection
        key_layout = QHBoxLayout()
        self.key_path_label = QLabel("Private Key File:")
        self.key_path_display = QLineEdit()
        self.key_path_display.setReadOnly(True)
        self.select_key_button = QPushButton("Select Private Key")
        self.select_key_button.clicked.connect(self._select_private_key)

        key_layout.addWidget(self.key_path_label)
        key_layout.addWidget(self.key_path_display)
        key_layout.addWidget(self.select_key_button)
        self.layout.addLayout(key_layout)

        # Add Key Pair Generation button
        key_gen_layout = QHBoxLayout()
        self.generate_keypair_button = QPushButton("Generate New Key Pair")
        self.generate_keypair_button.clicked.connect(self._generate_key_pair)
        self.key_size_label = QLabel("Key Size (bits):")
        self.key_size_combo = QComboBox()
        # Common RSA key sizes - 64, 128, 256 are insecure and not recommended for production use.
        self.key_size_combo.addItems(
            ["64", "128", "256", "1024", "2048", "4096", "8192", "16384"]
        )
        self.key_size_combo.setCurrentText("2048")  # Default to 2048

        key_gen_layout.addWidget(self.generate_keypair_button)
        key_gen_layout.addWidget(self.key_size_label)
        key_gen_layout.addWidget(self.key_size_combo)
        self.layout.addLayout(key_gen_layout)

        # Generate button
        self.generate_button = QPushButton("Generate License Key")
        self.generate_button.clicked.connect(self._generate_key)
        self.layout.addWidget(self.generate_button)

        # Output text area
        self.output_label = QLabel("Generated Key:")
        self.layout.addWidget(self.output_label)
        self.key_output = QTextEdit()
        self.key_output.setReadOnly(True)
        self.layout.addWidget(self.key_output)

        self.setLayout(self.layout)

        # Attempt to load existing keys on startup
        self._load_existing_keys()

    def _add_input_row(self, label_text, default_text=""):
        """Helper to add a label and line edit in a horizontal layout."""
        h_layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setText(default_text)
        h_layout.addWidget(label)
        h_layout.addWidget(line_edit)
        self.layout.addLayout(h_layout)
        return line_edit

    def _update_swap_param_input_state(self, state):
        """Updates the fixed_swap_param_input state based on checkbox."""
        # State is 2 if checked, 0 if unchecked
        is_checked = state == Qt.CheckState.Checked.value
        self.fixed_swap_param_input.setEnabled(not is_checked)
        self.fixed_swap_param_label.setEnabled(not is_checked)

        # Clear the fixed param input if switching to included
        if is_checked:
            self.fixed_swap_param_input.clear()

    def _select_private_key(self):
        """Opens a file dialog to select the private key file."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Private Key File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("PEM Files (*.pem);;All Files (*)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                selected_key_path = selected_files[0]
                try:
                    # Attempt to load the key immediately to provide feedback
                    # Assuming no password for simplicity in this UI example.
                    loaded_private_key = load_private_key_from_path(
                        selected_key_path, password=None
                    )
                    self.private_key = loaded_private_key
                    self.private_key_path = selected_key_path
                    self.key_path_display.setText(self.private_key_path)
                    QMessageBox.information(
                        self, "Key Loaded", "Private key loaded successfully."
                    )
                except FileNotFoundError:
                    QMessageBox.critical(
                        self, "Error Loading Key", "Private key file not found."
                    )
                    # Don't clear if a key was already loaded (e.g. automatically)
                    if not self.private_key:
                        self.key_path_display.clear()
                        self.private_key_path = ""
                except Exception as e:
                    QMessageBox.critical(
                        self, "Error Loading Key", f"Error loading private key: {e}"
                    )
                    # Don't clear if a key was already loaded (e.g. automatically)
                    if not self.private_key:
                        self.private_key = None
                        self.key_path_display.clear()
                        self.private_key_path = ""

    def _generate_key(self):
        """Generates the license key based on UI inputs."""
        if self.private_key is None:
            QMessageBox.warning(
                self,
                "Missing Private Key",
                "Please select and load a private key first.",
            )
            return

        try:
            # Read input values (with basic validation)
            license_plan = int(self.plan_input.text())
            duration_days = int(self.duration_input.text())
            key_holder_group = int(self.group_input.text())
            unique_license_id = int(self.unique_id_input.text())
            version_lock = int(self.version_lock_input.text())

            use_included_swap_param = self.use_included_swap_param_checkbox.isChecked()
            fixed_swap_param = None
            if not use_included_swap_param:
                fixed_swap_param_text = self.fixed_swap_param_input.text()
                if not fixed_swap_param_text:
                    raise ValueError(
                        "Fixed Swap Param cannot be empty when not using included param."
                    )
                fixed_swap_param = float(fixed_swap_param_text)
                if not 0.0 <= fixed_swap_param <= 1.0:
                    raise ValueError("Fixed Swap Param must be between 0.0 and 1.0")

            # Generate the key
            generated_key = generate_license_key(
                private_key=self.private_key,
                license_plan=license_plan,
                duration_days=duration_days,
                key_holder_group=key_holder_group,
                unique_license_id=unique_license_id,
                version_lock=version_lock,
                use_included_swap_param=use_included_swap_param,
                fixed_swap_param=fixed_swap_param,
            )

            # Display the generated key
            self.key_output.setText(generated_key)

        except ValueError as e:
            QMessageBox.warning(
                self, "Invalid Input", f"Please check your input values: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Error",
                f"An error occurred during key generation: {e}",
            )
            self.key_output.setText(f"Error: {e}")

    def _load_existing_keys(self):
        """Attempts to load private and public keys from default locations."""
        private_key_file = "./key"
        public_key_file = "./pub"

        if os.path.exists(private_key_file):
            try:
                # Assuming no password for the automatically loaded key
                loaded_private_key = load_private_key_from_path(
                    private_key_file, password=None
                )
                self.private_key = loaded_private_key
                self.private_key_path = private_key_file
                self.key_path_display.setText(self.private_key_path)
                print(f"Automatically loaded private key from {private_key_file}")

                # Optionally, load public key to verify the pair (not strictly needed for keygen)
                # if os.path.exists(public_key_file):
                #     try:
                #         loaded_public_key = load_public_key_from_path(public_key_file)
                #         # You could potentially store this if needed, or just use it for verification here
                #         print(f"Automatically loaded public key from {public_key_file}")
                #     except Exception as e:
                #          print(f"Error loading public key during startup: {e}")

            except Exception as e:
                print(f"Error loading private key during startup: {e}")
                self.private_key = None
                self.private_key_path = ""
                self.key_path_display.clear()
        else:
            print("No existing private key found at ./key")

    def _generate_key_pair(self):
        """Generates a new RSA key pair and saves them to ./key and ./pub."""
        private_key_file = "./key"
        public_key_file = "./pub"

        try:
            # Generate the key pair
            private_key, public_key = generate_rsa_key_pair()

            # Save the keys (without password for simplicity in this example)
            save_private_key_to_file(private_key, private_key_file, password=None)
            save_public_key_to_file(public_key, public_key_file)

            # Load the newly generated private key into the UI
            self.private_key = private_key
            self.private_key_path = private_key_file
            self.key_path_display.setText(self.private_key_path)

            QMessageBox.information(
                self,
                "Key Pair Generated",
                f"New key pair generated and saved to {private_key_file} and {public_key_file}.\nPrivate key loaded for signing.",
            )
            print(
                f"New key pair generated and saved to {private_key_file} and {public_key_file}."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Key Pair Generation Error",
                f"An error occurred during key pair generation: {e}",
            )
            print(f"Error generating key pair: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = KeyGenWindow()
    main_window.show()
    sys.exit(app.exec())
