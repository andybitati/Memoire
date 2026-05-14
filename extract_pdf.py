import PyPDF2

pdf_path = r"f:\Cours\Mémoire\Détection Autonome et Distribuée d’Anomalies dans les Journaux Systèmes et Réseaux à l’aide d’Agents Intelligents Multi-Tâches.pdf"

with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print(text)