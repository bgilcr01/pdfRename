Project is ready. Here's what's in place:                                                                                                    
                                                                                                                                               
  getTitle.py — single-file CLI tool with three stages:                                                                                        
                                                                                                                                               
  1. Extract — opens the PDF with pdfplumber, reads only the first page, and regex-matches a DOI (10.xxxx/...)                                 
  2. Fetch — queries https://api.crossref.org/works/{doi} for the title                                                                        
  3. Rename — sanitizes the title into a safe filename (strips bad chars, caps length at 200, avoids overwrites with a (2) counter)            
                                                                                                                                               
  **Usage**
  # Rename a single PDF
  python getTitle.py paper.pdf

  # Dry-run to preview renames without applying
  python getTitle.py paper.pdf --dry-run

  # Batch rename multiple PDFs
  python getTitle.py *.pdf

  requirements.txt lists the two dependencies (pdfplumber and requests), both already installed.

  The tool only reads the first page of each PDF, so it's fast even on large files. It handles missing DOIs, API failures, and filename
  collisions gracefully.