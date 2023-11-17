import secrets
import urequests

newsUrl = "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=" + secrets.newsapiAPI
user_agent = "Micropython"
headers = {
    "User-Agent": user_agent
}

def getNews():
    
    response = urequests.get(newsUrl, headers=headers)
    titles = []

    if response.status_code == 200:
        data = response.json()  # Parse the JSON response

        if "articles" in data:
            articles = data["articles"]
            for article in articles:
                if "title" in article:
                    titles.append(article["title"])
                else:
                    print("No title found in article.")
        else:
            print("No 'articles' key found in the JSON data.")
    else:
        print("Failed to retrieve data from the API.")
    
    response.close()  # Close the response when done
    return(titles)