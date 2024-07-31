import os
import cv2
from tkinter import Tk, filedialog, Label, Button, messagebox, Text, Scrollbar, RIGHT, Y, END, Frame, Canvas
from PIL import Image, ImageTk
import pytesseract
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the path for Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to extract text from an image
def extract_text(image_path):
    try:
        image = Image.open(image_path)
        custom_config = r'--oem 3 --psm 6 -l eng'
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process {image_path}: {str(e)}")
        return None

# Function to save extracted text to CSV
def save_to_csv(data):
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "extracted_texts.csv")
    df = pd.DataFrame(data, columns=["File Name", "Extracted Text"])
    df.to_csv(output_file, index=False)
    messagebox.showinfo("Info", f"Data saved to {output_file}")

# Function to capture image from camera
def capture_image_from_camera():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Press "Space" to Capture Image, "Esc" to Exit', frame)
        key = cv2.waitKey(1)
        if key == 27:  # Esc key to exit
            break
        elif key == 32:  # Space key to capture image
            if not os.path.exists("images"):
                os.makedirs("images")
            image_path = f"images/captured_image_{len(os.listdir('images')) + 1}.jpg"
            cv2.imwrite(image_path, frame)
            cap.release()
            cv2.destroyAllWindows()
            return image_path
    cap.release()
    cv2.destroyAllWindows()
    return None

# Document Scanner Application Class
class DocumentScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Scanner")
        self.root.geometry("1200x800")

        self.label = Label(root, text="Select Image(s) or Document(s) to Scan")
        self.label.pack(pady=10)

        self.select_btn = Button(root, text="Select Files", command=self.select_files)
        self.select_btn.pack(pady=5)

        self.capture_btn = Button(root, text="Capture from Camera", command=self.capture_from_camera)
        self.capture_btn.pack(pady=5)

        self.bulk_btn = Button(root, text="Bulk Scan", command=self.bulk_scan)
        self.bulk_btn.pack(pady=5)

        self.quit_btn = Button(root, text="Quit", command=root.quit)
        self.quit_btn.pack(pady=5)

        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.text_output = Text(root, wrap="word", yscrollcommand=self.scrollbar.set)
        self.text_output.pack(expand=True, fill='both')
        self.scrollbar.config(command=self.text_output.yview)

        self.image_frame = Frame(root)
        self.image_frame.pack(pady=10)

        self.data_model_btn = Button(root, text="Show Data Models", command=self.show_data_models)
        self.data_model_btn.pack(pady=5)

        self.canvas = Canvas(root)
        self.canvas.pack(expand=True, fill='both')
        self.image_labels = []

        self.captured_images = []
        self.extracted_texts = []

    def select_files(self):
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            data = []
            for file_path in file_paths:
                text = extract_text(file_path)
                if text:
                    self.text_output.insert(END, f"{file_path}:\n{text}\n\n")
                    data.append([os.path.basename(file_path), text])
                    self.display_image(file_path)
            self.extracted_texts.extend(data)
            save_to_csv(self.extracted_texts)

    def capture_from_camera(self):
        image_path = capture_image_from_camera()
        if image_path:
            self.display_image(image_path)
            text = extract_text(image_path)
            if text:
                self.text_output.insert(END, f"{image_path}:\n{text}\n\n")
                self.captured_images.append(image_path)
                self.extracted_texts.append([os.path.basename(image_path), text])
                save_to_csv(self.extracted_texts)

    def bulk_scan(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            data = []
            for file_path in files:
                text = extract_text(file_path)
                if text:
                    self.text_output.insert(END, f"{file_path}:\n{text}\n\n")
                    data.append([os.path.basename(file_path), text])
                    self.display_image(file_path)
            self.extracted_texts.extend(data)
            save_to_csv(self.extracted_texts)

    def display_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)

        panel = Label(self.image_frame, image=img)
        panel.image = img  # keep a reference to avoid garbage collection
        panel.pack(side="left", padx=5, pady=5)
        self.image_labels.append(panel)

    def show_data_models(self):
        if self.extracted_texts:
            df = pd.DataFrame(self.extracted_texts, columns=["File Name", "Extracted Text"])
            df['Text Length'] = df['Extracted Text'].apply(len)
            plt.figure(figsize=(10, 6))
            sns.barplot(x='File Name', y='Text Length', data=df)
            plt.xticks(rotation=90)
            plt.title('Text Length of Each Document')
            plt.show()
        else:
            messagebox.showinfo("Info", "No data to display")

if __name__ == "__main__":
    # Ensure 'images' directory exists
    if not os.path.exists('images'):
        os.makedirs('images')
    
    root = Tk()
    app = DocumentScannerApp(root)
    root.mainloop()
