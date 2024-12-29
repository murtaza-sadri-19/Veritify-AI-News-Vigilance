# **TruthTrack: AI Vigilance for Reliable Information**

### Overview
TruthTrack is an innovative project aimed at analyzing and categorizing news articles to enhance media literacy and combat misinformation. By utilizing advanced machine learning techniques, TruthTrack empowers users to evaluate the credibility of news sources and understand media biases, ultimately fostering a more informed society.

### Key Features
- **News Categorization**: Automatically classify news articles into relevant topics using Latent Dirichlet Allocation (LDA) and other machine learning models.
- **Similarity Analysis**: Assess the similarity between different news articles, helping users identify related content and potential biases.
- **Web Scraping**: Gather data from various news sources, including The Hindu and PolitiFact, to create a rich dataset for analysis.
- **Interactive Visualizations**: Utilize Jupyter Notebooks for interactive exploration of data and model results, making it easier to understand complex relationships within the news.

### Directory Structure
The project is organized as follows:

```
murtaza-sadri-19-TruthTrack/
├── app.py
├── demo.py
├── google_search_results.csv
├── requirements.txt
├── README.md
├── News Proto/
│   ├── PAM based model.ipynb
│   └── news.zip
├── News Topic/
│   ├── Similarity_news.ipynb
│   ├── lda_model.model
│   └── ...                    
├── Dataset/
│   ├── TheHinduCricket/
│   ├── PolitiFact/
│   └── ...
└── templates/
    ├── index.html
    └── main.html
```

### Installation Instructions
To set up TruthTrack locally, follow these steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/murtaza-sadri-19/TruthTrack.git
   cd TruthTrack
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Usage Guidelines
To run the application, execute:
```bash
python app.py
```
Explore the capabilities of TruthTrack through the demo script or by interacting with the Jupyter Notebooks located in the `News Proto/` and `News Topic/` directories.

### Future Enhancements
- **User Interface Improvements**: Enhance the web interface for a better user experience.
- **Additional Data Sources**: Integrate more diverse news sources to broaden analysis.
- **Advanced Analytics**: Implement deeper analytical features such as sentiment analysis.

---

TruthTrack is designed not only as a tool for analysis but also as an educational resource to promote understanding of media content. Join us in our mission to enhance media literacy!
