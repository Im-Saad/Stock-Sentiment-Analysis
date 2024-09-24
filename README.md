This project analyzes sentiment in comments and posts from various subreddits. It uses the Python Reddit API Wrapper (PRAW) to fetch data, 
processes it with Natural Language Processing (NLP) tools, and visualizes sentiment trends for mentioned stocks. 
The analysis focuses on comments related to stock tickers, providing insights into the sentiment surrounding various investments.

## Project Structure

Scripts

`config.py`
-This script contains configuration variables that are crucial for connecting to the Reddit API and customizing the analysis parameters.

`data.py`
-This script defines the data structures and constants used throughout the project, including lists of stock symbols and any necessary filtering conditions.

`reddit_sentiment_analysis.py`
- Connects to the Reddit API using credentials from `config.py`.
- Extracts posts and comments from the specified subreddits.
- Analyzes the sentiment of the comments using NLTK's VADER sentiment analysis.
- Visualizes the analysis results using Matplotlib.

`run.py`
-To run the `reddit_sentiment_analysis.py` script using a subprocess.

Configure your Reddit API credentials:
-Open `config.py` and replace `'your-client-id'`, `'your-client-secret'`, and `'your-user-agent'` with your Reddit API credentials.

Run the analysis:
-You can start the sentiment analysis by running the following command:
-The results are displayed in the console and through plots.
