import pikepdf

def decrypt_pdf(input_pdf_path, output_pdf_path, password=None):
    try:
        if password:
            pdf = pikepdf.open(input_pdf_path, password=password)
        else:
            pdf = pikepdf.open(input_pdf_path) # Attempt to open without password

        pdf.save(output_pdf_path)
        print(f"PDF successfully decrypted and saved to: {output_pdf_path}")
        return True
    except pikepdf.PasswordError:
        print(f"Error: Incorrect password for {input_pdf_path}")
        return False
    except Exception as e:
        print(f"Error decrypting PDF: {e}")
        return False

if __name__ == "__main__":
    input_file = "D:\geminiCLI\MT6631 Design Notice V1.2_20200622.pdf"
    output_file = "D:\geminiCLI\MT6631 Design Notice V1.2_20200622_decrypted.pdf"
    
    # Attempt to decrypt without a password first
    if not decrypt_pdf(input_file, output_file):
        print("Attempting to decrypt with a common password (e.g., 'password')...")
        # If the above fails, you might prompt the user for a password or try common ones
        # For this task, we assume no password or a simple one if needed.
        # If the PDF is protected by a permission password (not open password),
        # pikepdf.open() without a password should still work to remove restrictions.
        # If it's an open password, you'll need the correct password.
        pass
