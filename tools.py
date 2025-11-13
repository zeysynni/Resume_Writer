import pypandoc
import os
from agents import Agent, function_tool, Runner, trace, Tool
from typing import Optional

@function_tool
def tex_to_pdf(tex_file_path : str, output_pdf_path: Optional[str]=None) -> str:
    """
    Converts a .tex file into a .pdf file and save it locally in the same folder.
    """
    # Default output name if not provided
    if output_pdf_path is None:
        base_name = os.path.splitext(tex_file_path)[0]
        output_pdf_path = base_name + ".pdf"

    # Convert .tex → .pdf
    pypandoc.convert_text(
        open(tex_file_path, encoding="utf-8").read(),
        'pdf',
        format='latex',
        outputfile=output_pdf_path,
        extra_args=['--standalone']
    )

    print(f"✅ Converted {tex_file_path} → {output_pdf_path}")
    return output_pdf_path


if __name__ == "__main__":
    tex_path = "sandbox/Resume/Zeyuan_Sun_Resume.tex"
    tex_to_pdf(tex_path)