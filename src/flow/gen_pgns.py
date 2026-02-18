from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os, re

#directorio base y generated_files
BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")
FILES_DIR = os.path.join(BASE_DIR,"generated_files")
    
def keyword_gen(text):
    print("\n************** WORDCLOUD GENERATION **************")


    
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

    
    os.makedirs(FILES_DIR,exist_ok=True)
    plt.savefig(f"{FILES_DIR}/keyword_cloud.png")
    #plt.show()

    print(f"WordCloud guardado en {FILES_DIR} como keyword_cloud.png\n")
    


def figures_gen(papers, counts):
    print("\n************** FIGURE VISUALIZATION GENERATION **************")

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

    os.makedirs(f"{FILES_DIR}",exist_ok=True)
    plt.savefig(f"{FILES_DIR}/figures_visualization.png")
    #plt.show()
    
    print(f"Visualizacion de figuras guardada en {FILES_DIR} como figures_visualization.png\n")
