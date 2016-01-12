# reverse_food_project
Building reverse recipe finder based on ingredients search and relevance scores between ingredients (based on data from food.com).

Pipeline:
- Scraping ingredients list from food.com (~1000 ingredients)
- Using ingredients search as starting list to scrape recipes and store into mongoDB (~500k recipes)

To dos:
- Building adjacency matrix between recipes and ingredients weighted by recipe rating
- Building relevance scores applying random walks algorithm (http://people.cs.pitt.edu/~huiming/research/icdm05.pdf)
- Building recipe search interface suggesting iteratively top 10 ingredients to add based on first ingredient search 
