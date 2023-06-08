# AI-Paper-Reccomentation

## Requirements
- python <3.10 and ptyhon >=3.6
- Semantic Scholar API key
- OpenAI API key (optional)

## Description
The AI-Based Paper Recommendation Tool is an innovative project designed to simplify the process of discovering relevant research papers in the field of interest. Leveraging the power of artificial intelligence (AI), this tool integrates various technologies and APIs to provide users with personalized paper recommendations and concise summaries.

## Features

1. **Semantic Scholar API Integration**: The tool utilizes the Semantic Scholar API to search for research papers based on user queries. The API provides a vast collection of scholarly articles, ensuring comprehensive coverage across various disciplines.

2. **Refy Integration for Recommendations**: To enhance the user experience, the tool incorporates the Refy recommendation engine. Refy analyzes user preferences and browsing history to generate personalized recommendations, ensuring that users discover papers aligned with their interests.

3. **OpenAI Da Vinci Model for Summarization**: The tool leverages the powerful OpenAI Da Vinci model, a state-of-the-art language model, to automatically summarize research papers. This feature saves users valuable time by providing concise and informative summaries, allowing them to quickly assess the relevance and significance of a paper.

4. **Pinecone Vectorstore & Paper Questioning**: don't remember where you read about a specific topic? Just ask with Llama Indexing system. This option requires a free Pinecone API.

## How It Works

1. **Query Submission**: Users can input their research interests or specific topics of interest into the tool's user interface.

2. **Semantic Scholar API Search**: The tool utilizes the Semantic Scholar API to search for papers related to the user's query. It retrieves relevant metadata such as titles, authors, abstracts, and publication details.

3. **Refy Recommendation Engine**: Based on the user's query and browsing history, Refy generates personalized recommendations from the retrieved papers. These recommendations prioritize relevance and help users discover papers that align with their interests.

4. **Paper Summarization**: To assist users in quickly grasping the main ideas of a paper, the tool employs the OpenAI Da Vinci model to generate concise summaries. The model extracts key information from the paper, condensing it into a brief and coherent summary.

## Benefits

- **Time-Efficient Research**: By utilizing AI-powered algorithms, the tool significantly reduces the time required to discover, evaluate, and understand research papers.

- **Personalized Recommendations**: The integration of the Refy recommendation engine ensures that users receive tailored recommendations based on their individual interests and preferences.

The AI-Based Paper Recommendation Tool combines cutting-edge technologies and APIs to revolutionize the way researchers discover and interact with scholarly papers. Whether you are an academic, student, or industry professional, this tool empowers you to stay up-to-date with the latest research in your field while saving you time and effort.

## Work in progress
- [ ] Make refy suggestion sytem to work automatically with manually added PDFs (need to extract the DOI, pages, ecc automatically)(alternatively you can add them manually to the .bib)
