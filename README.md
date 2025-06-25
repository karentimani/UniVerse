# UniVerse
![UniVerse Logo](images/uniVerse.png)

A toolkit for collecting, processing, and exploring university data, developed by Rim Chehade and Karen Timiani.

---

## About

UniVerse is a collection of notebooks and scripts to:

- **Gather** data on Lebanese universities (LU, LAU, LIU…)
- **Clean & preprocess** raw CSV/JSON dumps
- **Visualize** co-authorship networks, enrollment trends, etc.
- **Export** polished tables and plots for reports

---

## Code & Hosting

The main codebase and backend are hosted on Kaggle. This GitHub repo will serve as the front-facing project, pulling in core notebooks and scripts as needed.

- **Kaggle notebooks:** [https://www.kaggle.com/karentimani/agenitic-rag](https://www.kaggle.com/karentimani/agenitic-rag)
- **Live backend URL:** Uses an ngrok tunnel provided in the Kaggle notebook (update the `ngrok_url` in your frontend code when it changes)

To integrate:

1. Open the Kaggle notebook and click **Copy & Edit** to clone into your Kaggle account.
2. Download the notebook and any generated scripts via **File > Download**.
3. Commit those files into this GitHub repo under the appropriate folders (e.g., `Data Collection/`, `Data Processing/`, `backend/`).
