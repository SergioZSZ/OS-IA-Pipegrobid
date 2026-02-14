import os

def gen_txt(links_dict):
    print("\n************** LINKS TXT GENERATION **************")

    os.makedirs("generated_files", exist_ok=True)

    with open("generated_files/links_per_paper.txt", "w", encoding="utf-8") as txt:

        for paper, links in links_dict.items():

            txt.write(f"{paper}\n")
            txt.write("-" * len(paper) + "\n")

            if links:
                for link in links:
                    txt.write(f"  - {link}\n")
            else:
                txt.write("  No links found.\n")

            txt.write("\n")

    print(f"Links guardados en generated_files como links_per_paper.txt\n")
