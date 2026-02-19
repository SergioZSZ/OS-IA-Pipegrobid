from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os, re

    
def keyword_gen(text: str, dir_files: str) -> None:
    
    #Generacion del WorldCloud
    wordcloud = WordCloud(
        width=1600,
        height=800,
        background_color="white",
        colormap="viridis"
    ).generate(text)

    plt.figure(figsize=(12,6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(f"{dir_files}/keyword_cloud.png")
    #plt.show()

    print(f"\nWordCloud guardado en 'generated_files' como keyword_cloud.png\n")
    




def figures_gen(papers: list[str], counts: list[int], dir_files: str) -> None:
    #limpieza de los nombres de los papers xml
    papers_clean = [
        os.path.basename(p).replace(".tei.xml", "")
        for p in papers
    ]
        
    #imagen
    plt.figure(figsize=(16,8))
    plt.bar(papers_clean, counts)
    plt.xticks(rotation=45)
    plt.ylabel("nº de figuras")
    plt.title("figuras/paper")

    os.makedirs(f"{dir_files}",exist_ok=True)
    plt.savefig(f"{dir_files}/figures_visualization.png")
    #plt.show()
    
    print(f"Visualizacion de figuras guardada en 'generated_files' como figures_visualization.png\n")





def gen_txt(links_dict: dict, dir_files: str) -> None:

    with open(f"{dir_files}/links_per_paper.txt", "w", encoding="utf-8") as txt:

        for paper, links in links_dict.items():
            
            txt.write(f"{os.path.basename(paper).replace(".tei.xml", "")}:\n\n")

            if links:
                for link in links:
                    txt.write(f"  - {link}\n")
            else:
                txt.write("  No links found.\n")
            txt.write("-------------------------------------------------------------------------------------------------\n")
            txt.write("\n")

    print(f"Links guardados en '/generated_files' como links_per_paper.txt\n")
