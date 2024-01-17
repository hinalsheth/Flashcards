from openai import OpenAI
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from rich.panel import Panel
import PyPDF2
import argparse


def read_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() for page in reader.pages)
        return text


def summarize_text(client, model, text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text into key points separating each with '- ':\n\n{text}",
            }
        ],
        model=model,
    )

    response = chat_completion.choices[0].message.content

    # Find the first point
    summary = response[response.find("-") :]

    # Remove leading - from each point
    return [point.strip("- ") for point in summary.split("\n")]


def print_flashcards(flashcards):
    console = Console()
    print()

    for i, card in enumerate(flashcards):
        panel = Panel(
            card,
            title=f"Flashcard {i + 1}",
            box=ROUNDED,
            border_style="bright_yellow",
        )
        console.print(panel)
        print("\n")


def print_flashcards2(flashcards):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Flashcard #", style="dim")
    table.add_column("Summary")

    for i, card in enumerate(flashcards):
        table.add_row(str(i + 1), card)

    console.print(table)


def main():
    try:
        from secret import API_KEY

        client = OpenAI(api_key=API_KEY)
    except ImportError:
        print("Please create a secret.py file with your OpenAI API key")
        return

    parser = argparse.ArgumentParser(description="Create flashcards from a PDF file")
    parser.add_argument("file", type=str, help="Path to file [.pdf or .txt supported]")
    parser.add_argument(
        "--model",
        type=str,
        help="OpenAI model to use",
        choices=["gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"],
        default="gpt-4",
    )
    args = parser.parse_args()

    if not args.file:
        print("Please provide a file path")
        return

    # Read the file
    if args.file.endswith(".pdf"):
        pdf_text = read_pdf(args.file)
    elif args.file.endswith(".txt"):
        with open(args.file, "r") as file:
            pdf_text = file.read()
    else:
        print("Please provide a .pdf or .txt file")
        return

    flashcards = summarize_text(client, args.model, pdf_text)

    print_flashcards(flashcards)


if __name__ == "__main__":
    main()
