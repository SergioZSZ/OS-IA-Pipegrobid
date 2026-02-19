import os

def gen_env(base_dir: str) -> dict:
    
    dir_pdfs = os.path.join(base_dir,"pdfs")
    dir_xmls = os.path.join(base_dir,"xmls")
    dir_files = os.path.join(base_dir,"generated_files")
    
    os.makedirs(dir_pdfs,  exist_ok=True)
    os.makedirs(dir_xmls,  exist_ok=True)
    os.makedirs(dir_files,  exist_ok=True)
    
    return {
        "pdfs":dir_pdfs,
        "xmls":dir_xmls,
        "files":dir_files,
    }

    