import os


#directorio base y generated_files
BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")
FILES_DIR = os.path.join(BASE_DIR,"generated_files")

def gen_txt(links_dict):
    print("\n************** LINKS TXT GENERATION **************")

    os.makedirs(FILES_DIR, exist_ok=True)

    with open(f"{FILES_DIR}/links_per_paper.txt", "w", encoding="utf-8") as txt:

        for paper, links in links_dict.items():

            txt.write(f"{paper}\n")
            txt.write("-" * len(paper) + "\n")

            if links:
                for link in links:
                    txt.write(f"  - {link}\n")
            else:
                txt.write("  No links found.\n")

            txt.write("\n")

    print(f"Links guardados en {FILES_DIR} como links_per_paper.txt\n")
