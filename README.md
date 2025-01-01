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
Directory structure:
└── murtaza-sadri-19-TruthTrack/
    ├── Prediction.py
    ├── demo.py
    ├── google_search_results.csv
    ├── app.py
    ├── truthteller_application/
    │   ├── .vscode/
    │   │   ├── diff/
    │   │   │   └── vulsCount.txt
    │   │   └── settings.json
    │   ├── linux/
    │   │   ├── my_application.h
    │   │   ├── .gitignore
    │   │   ├── flutter/
    │   │   │   ├── generated_plugins.cmake
    │   │   │   ├── CMakeLists.txt
    │   │   │   └── generated_plugin_registrant.h
    │   │   └── CMakeLists.txt
    │   ├── pubspec.lock
    │   ├── .gitignore
    │   ├── assets/
    │   ├── ios/
    │   │   ├── .gitignore
    │   │   ├── Runner/
    │   │   │   ├── AppDelegate.swift
    │   │   │   ├── Base.lproj/
    │   │   │   │   ├── Main.storyboard
    │   │   │   │   └── LaunchScreen.storyboard
    │   │   │   ├── Assets.xcassets/
    │   │   │   │   ├── AppIcon.appiconset/
    │   │   │   │   │   └── Contents.json
    │   │   │   │   └── LaunchImage.imageset/
    │   │   │   │       ├── README.md
    │   │   │   │       └── Contents.json
    │   │   │   ├── Runner-Bridging-Header.h
    │   │   │   └── Info.plist
    │   │   ├── Flutter/
    │   │   │   ├── Debug.xcconfig
    │   │   │   ├── Release.xcconfig
    │   │   │   └── AppFrameworkInfo.plist
    │   │   ├── Runner.xcodeproj/
    │   │   │   ├── project.xcworkspace/
    │   │   │   │   ├── contents.xcworkspacedata
    │   │   │   │   └── xcshareddata/
    │   │   │   │       ├── IDEWorkspaceChecks.plist
    │   │   │   │       └── WorkspaceSettings.xcsettings
    │   │   │   ├── project.pbxproj
    │   │   │   └── xcshareddata/
    │   │   │       └── xcschemes/
    │   │   │           └── Runner.xcscheme
    │   │   ├── Runner.xcworkspace/
    │   │   │   ├── contents.xcworkspacedata
    │   │   │   └── xcshareddata/
    │   │   │       ├── IDEWorkspaceChecks.plist
    │   │   │       └── WorkspaceSettings.xcsettings
    │   │   └── RunnerTests/
    │   │       └── RunnerTests.swift
    │   ├── test/
    │   │   └── widget_test.dart
    │   ├── pubspec.yaml
    │   ├── lib/
    │   │   └── main.dart
    │   ├── analysis_options.yaml
    │   ├── windows/
    │   │   ├── runner/
    │   │   │   ├── utils.cpp
    │   │   │   ├── win32_window.h
    │   │   │   ├── utils.h
    │   │   │   ├── win32_window.cpp
    │   │   │   ├── flutter_window.h
    │   │   │   ├── flutter_window.cpp
    │   │   │   ├── CMakeLists.txt
    │   │   │   ├── main.cpp
    │   │   │   ├── Runner.rc
    │   │   │   └── resource.h
    │   │   ├── .gitignore
    │   │   ├── flutter/
    │   │   │   ├── generated_plugins.cmake
    │   │   │   ├── CMakeLists.txt
    │   │   │   └── generated_plugin_registrant.h
    │   │   └── CMakeLists.txt
    │   ├── macos/
    │   │   ├── .gitignore
    │   │   ├── Runner/
    │   │   │   ├── AppDelegate.swift
    │   │   │   ├── Base.lproj/
    │   │   │   │   └── MainMenu.xib
    │   │   │   ├── Configs/
    │   │   │   │   ├── Debug.xcconfig
    │   │   │   │   ├── Release.xcconfig
    │   │   │   │   ├── Warnings.xcconfig
    │   │   │   │   └── AppInfo.xcconfig
    │   │   │   ├── Release.entitlements
    │   │   │   ├── MainFlutterWindow.swift
    │   │   │   ├── DebugProfile.entitlements
    │   │   │   ├── Assets.xcassets/
    │   │   │   │   └── AppIcon.appiconset/
    │   │   │   │       └── Contents.json
    │   │   │   └── Info.plist
    │   │   ├── Flutter/
    │   │   │   ├── GeneratedPluginRegistrant.swift
    │   │   │   ├── Flutter-Debug.xcconfig
    │   │   │   └── Flutter-Release.xcconfig
    │   │   ├── Runner.xcodeproj/
    │   │   │   ├── project.xcworkspace/
    │   │   │   │   └── xcshareddata/
    │   │   │   │       └── IDEWorkspaceChecks.plist
    │   │   │   ├── project.pbxproj
    │   │   │   └── xcshareddata/
    │   │   │       └── xcschemes/
    │   │   │           └── Runner.xcscheme
    │   │   ├── Runner.xcworkspace/
    │   │   │   ├── contents.xcworkspacedata
    │   │   │   └── xcshareddata/
    │   │   │       └── IDEWorkspaceChecks.plist
    │   │   └── RunnerTests/
    │   │       └── RunnerTests.swift
    │   ├── android/
    │   │   ├── .gitignore
    │   │   └── app/
    │   │       └── src/
    │   │           ├── main/
    │   │           │   ├── AndroidManifest.xml
    │   │           │   ├── res/
    │   │           │   │   ├── mipmap-mdpi/
    │   │           │   │   ├── mipmap-xxxhdpi/
    │   │           │   │   ├── mipmap-hdpi/
    │   │           │   │   ├── mipmap-xxhdpi/
    │   │           │   │   ├── drawable/
    │   │           │   │   │   └── launch_background.xml
    │   │           │   │   ├── mipmap-xhdpi/
    │   │           │   │   ├── drawable-v21/
    │   │           │   │   │   └── launch_background.xml
    │   │           │   │   ├── values-night/
    │   │           │   │   │   └── styles.xml
    │   │           │   │   └── values/
    │   │           │   │       └── styles.xml
    │   │           │   └── kotlin/
    │   │           │       └── com/
    │   │           │           └── example/
    │   │           │               └── flutter_application_1/
    │   │           │                   └── MainActivity.kt
    │   │           ├── debug/
    │   │           │   └── AndroidManifest.xml
    │   │           └── profile/
    │   │               └── AndroidManifest.xml
    │   ├── web/
    │   │   ├── manifest.json
    │   │   ├── index.html
    │   │   └── icons/
    │   ├── .metadata
    │   └── README.md
    ├── News Proto/
    │   ├── PAM based model.ipynb
    │   ├── nmf_model_params.json
    │   ├── news.tsv
    │   ├── news.zip
    │   ├── tfidf_vectorizer.pkl
    │   ├── news.csv
    │   └── nmf_model.pkl
    ├── truthtell_extension/
    │   ├── manifest.json
    │   ├── background.js
    │   ├── popup.js
    │   ├── content.js
    │   ├── popup.html
    │   ├── icons/
    │   └── README.md
    ├── requirements.txt
    ├── News Topic/
    │   ├── news_topic.zip
    │   ├── lda_model.model.expElogbeta.npy
    │   ├── News_Topic.md
    │   ├── Similarity_news.ipynb
    │   ├── lda_model.model.state
    │   ├── lda_model.model
    │   ├── lda_model.model.id2word
    │   ├── categorized_news.zip
    │   ├── .idea/
    │   │   ├── Topic_Modelling_news.iml
    │   │   ├── misc.xml
    │   │   ├── .gitignore
    │   │   ├── modules.xml
    │   │   ├── workspace.xml
    │   │   ├── inspectionProfiles/
    │   │   │   └── profiles_settings.xml
    │   │   └── jupyter-settings.xml
    │   ├── lda_model1.json
    │   ├── lda_model.json
    │   ├── lda_dictionary.txt
    │   ├── News_Topic.ipynb
    │   └── News_Topic_.ipynb
    ├── similarity.py
    ├── Dataset/
    │   ├── TheHinduCricket/
    │   │   ├── Web_Scraping.ipynb
    │   │   └── Web_Scrapping_Hindu.csv
    │   ├── PolitiFact/
    │   │   ├── FactChecker_Dataset.csv
    │   │   └── ScrapCode.ipynb
    │   ├── Web_Scrapping_factcheck.csv
    │   ├── Web_Scrapping_Snopes.csv
    │   └── cricket.ipynb
    ├── News_Topic_.ipynb
    ├── README.md
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
