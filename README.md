# reverse_food_project
Building reverse recipe finder based on ingredients search and relevance scores between ingredients (based on data from food.com).
 
Pipeline:
- Scraping ingredients list from food.com (~1000 ingredients)
- Using ingredients search as starting list to scrape recipes and 
- Storing into mongoDB (~500k recipes)
- Calculating adjacency matrix weighted by ratings
- Calculating relevance scores based on random walks algorithm (http://people.cs.pitt.edu/~huiming/research/icdm05.pdf)

Final planned usage:
* Enter ingredient
* Filter recipe type (breakfast, cheap, vegetarian, etc.)
* While [Number of compatible recipes] > 3: Pick ingredient to add amongs selection of 10 most relevant
* Pick recipe with selected ingredients
