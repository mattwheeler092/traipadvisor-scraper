# TripAdvisor Scraper

Travo.ai is an incredible travel planning app designed to make your trip planning experience seamless and personalized. By simply providing text prompts describing your desired activities, Travo.ai generates customized travel itineraries just for you!

With access to a vast database of over 120,000 activities from 130 cities worldwide, sourced directly from TripAdviser, Travo.ai ensures that you have access to the best recommendations for your travel adventures ([more details](https://github.com/mattwheeler092/travo-ai-recommendation-engine)). You can visit our  [website](https://eclectic-brioche-a372fe.netlify.app/) to try it out for yourself!

This GitHub repository encompasses the code required to scrape and process the 120,000 TripAdvisor events and activities. Topics covered include:

- [Project Description](#project-description)
- [Recommender Architecture](#pipeline-diagram)
- [Dev Installation](#dev-installation)


![](https://github.com/mattwheeler092/travo-ai-recommendation-engine/blob/main/images/travo-ai-demo.gif)

## Project Description

Travo.ai is a personalized trip planning app that generates customized itineraries based on user-provided descriptions of their desired activities. We collected a vast array of activities and events from TripAdvisor to provide recommendations to users.

Our scalable Python pipeline, automated using Airflow, efficiently scraped events and activities from TripAdvisor by sending custom POST requests. We processed the retrieved events, filtering out invalid ones without descriptions or location information. We gathered details such as event description, location, rating, duration, and website.

As discussed in the recommendation [repo](https://github.com/mattwheeler092/travo-ai-recommendation-engine), Travo.ai's recommendation engine utilized cosine similarity between vector representations of TripAdvisor activity descriptions and user text prompts. We created these vector embeddings using the OpenAI embedding API, which embedded the event description and associated category tags.

The processed event data and vector embeddings were stored in a Pinecone database for quick querying of similar vectors. Additionally, a backup of the data was stored in a GCS bucket. With this approach, we had gathered over 120,000 activities from 130 cities. You can refer to the **Pipeline Diagram** for a visual representation of our scraper's workflow.


## Pipeline Diagram

![](https://github.com/mattwheeler092/tripadvisor-scraper/blob/main/images/Screenshot%202023-05-24%20at%2017.54.51.png)

## Dev Installation

If you want to use this code for your own use, follow these steps in the repository root directory to create and activate the Python virtual environment for further development:

1. Run the following command to set up the virtual environment. You only need to run this once:
   - `make setup`

2. Activate the virtual environment by running the command:
   - `source env/bin/activate`

**NOTE:** If you need to include new packages for your recommendation engine, make sure to include them in the `requirements.txt` file