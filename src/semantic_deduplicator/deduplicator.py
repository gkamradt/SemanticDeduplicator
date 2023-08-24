import os
import warnings
from typing import List

import numpy as np
import openai
from dotenv import load_dotenv


load_dotenv()


class SemanticDeduplicator:
    def __init__(
        self,
        similarity_background="",
        final_similarity_threshold=0.8,
        cosine_similarity_threshold=0.75,
        openai_api_key="",
    ):
        self.deduplicated_items_list = []
        self.cosine_similarity_threshold = cosine_similarity_threshold
        self.final_similarity_threshold = final_similarity_threshold
        self.similarity_background = similarity_background
        self.similarity_model = "gpt-4"
        self.action_prefix = " **Action** "

        # If the API key is provided during initialization, use it. Else, get it from the environment variable.
        openai.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set in the environment variable 'OPENAI_API_KEY'"
            )

        if similarity_background == "":
            warnings.warn(
                "The 'similarity_background' variable is empty. It's recommended to provide context on your data for "
                "better results."
            )

    def add_item(self, item):
        """Adds an item to the deduplicated_items_list, or combines it with an existing item if it is similar enough.
        Not currently supported: Extracting multiple items in a single add"""

        # Check to see if your items list has any data
        if len(self.deduplicated_items_list) == 0:
            self.add_item_to_new_list(item)
        else:
            self.add_item_to_existing_list(item)

        print("")

        return

    def add_item_to_existing_list(self, item):
        # If your deduplist has data, then check to see if the item is similar to any of the existing items
        similar_item = self.semantic_search(item)

        if similar_item is not None:
            # If you have a similar item, then combine your candidate item w/ the existing one
            self.combine_with_existing_item(item, similar_item)
        else:
            # If not, add your candidate item to the dedup list
            self.add_new_item_to_deduplicated_list(item)

    def add_item_to_new_list(self, item):
        self.add_new_item_to_deduplicated_list(item)

        return

    def combine_with_existing_item(self, item, similar_item):
        # Just taking the top item to make it easy for now.
        # Will edit this later if it becomes an issue

        # Get the index of the item in the existing list
        index_of_item_being_edited = next(
            i
            for i, item in enumerate(self.deduplicated_items_list)
            if item["formatted_name"] == similar_item
        )

        new_item_name = self.get_new_name_for_combine_items(item, similar_item)  # Here
        new_item_vector = self.get_embedding(new_item_name)

        self.deduplicated_items_list[index_of_item_being_edited][
            "formatted_name"
        ] = new_item_name
        self.deduplicated_items_list[index_of_item_being_edited][
            "item_embedding"
        ] = new_item_vector
        self.deduplicated_items_list[index_of_item_being_edited][
            "original_items_list"
        ].append(item)
        self.deduplicated_items_list[index_of_item_being_edited][
            "num_original_items"
        ] += 1

        print(f"{self.action_prefix}Changed Item {similar_item} to {new_item_name}")

    def add_new_item_to_deduplicated_list(self, item):
        # Transform the raw item name to a more standarized format
        formatted_item_name = self.transform_item_name(item)

        # Get the embedding of the item
        item_embedding = self.get_embedding(formatted_item_name)

        self.deduplicated_items_list.append(
            {
                "formatted_name": formatted_item_name,
                "item_embedding": item_embedding,
                "original_items_list": [
                    item
                ],  # This will hold more names in the future,
                "num_original_items": 1,
            }
        )
        return

    def transform_item_name(self, item):
        # We can upgrade this to function calling
        """A string that comes in might not be in a clear format. This function helps standardize names and extract
        requests"""
        system_prompt = f""" Your goal is to reword a user input according to their instructions. Their instructions
        will describe a desired goal or output and you should transform the phrase or item to the best of your ability

        % Start of user's background
        {self.similarity_background}
        % End of user's background

        Respond with nothing else besides the new item name.
        No not include any labels, or double-quotes
        """

        human_prompt = f"""
        {item}
        """

        new_item_name = self.call_llm(
            system_prompt=system_prompt, human_prompt=human_prompt
        )

        return new_item_name

    def add_items(self, items: List[str]):
        for item in items:
            self.add_item(item)

        print(f"Done adding {len(items)} items")

    @staticmethod
    def call_llm(
        system_prompt="You are a helpful assistant.",
        human_prompt="Hello!",
        function_schema=[],
        model="gpt-4-0613",
    ):
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt},
            ],
        }
        if function_schema:
            params["functions"] = function_schema

        completion = openai.ChatCompletion.create(**params)
        return completion.choices[0].message["content"]

    def get_new_name_for_combine_items(self, item, found_item):
        system_prompt = f"""
        Your goal is to combine two different similar items together. They have been deemed similar and should be
        combined.
        Example: "I went to the park" & "I went to outside" > "I went outside"
        Example: "I want dark mode" & "I want two modes, light and dark" > "I want dark mode"

        Make sure you lose minimal information about the two items.

        Here is background information from the user about the items.
        Make sure to listen to the user and take their context into account.

        % Start of background
        {self.similarity_background}
        % End of background

        Respond with nothing else besides the new item name.
        No not include any labels, or double-quotes
        """

        human_prompt = f"""
        New Item: {item}
        Existing Item: {found_item}
        """

        new_item_name = self.call_llm(
            system_prompt=system_prompt, human_prompt=human_prompt
        )

        new_item_name_formatted = self.transform_item_name(new_item_name)

        return new_item_name_formatted

    def delete_item(self, item):
        similar_item = self.semantic_search(item)

        if similar_item is None:
            print("No item found to delete")

        else:
            index_of_item_being_deleted = next(
                i
                for i, item in enumerate(self.deduplicated_items_list)
                if item["formatted_name"] == similar_item
            )

            self.deduplicated_items_list.pop(index_of_item_being_deleted)

            print(f"Droped item: {similar_item}")

        return

    def cosine_similarity(self, item, existing_item):
        # Calculate the dot product of the two vectors

        vector_1 = self.get_embedding(item)
        vector_2 = self.get_embedding(existing_item)

        dot_product = np.dot(vector_1, vector_2)

        # Calculate the norms of each vector
        norm_1 = np.linalg.norm(vector_1)
        norm_2 = np.linalg.norm(vector_2)

        # Calculate the cosine similarity
        cosine_similarity = dot_product / (norm_1 * norm_2)

        return cosine_similarity

    def get_cosine_similarity(self, item, existing_item):
        cosine_similarity_score = self.cosine_similarity(item, existing_item)

        return cosine_similarity_score

    def get_llm_similarity(self, item_1, item_2):
        system_prompt = f"""
        Your goal is to give a rating as to how semantically similar to items or phrases are together.
        You will be given two phrases.
        Words which are interchangable should be considered similar. Ex: Awesome, cool, great, wonderful are all similar

        Here is background information from the user about the items.
        Make sure to listen to the user and take their context into account.

        % Start of background
        {self.similarity_background}
        % End of background

        Respond with only the number 0-100

        100=Exact same phrase
        0=Opposite phrase

        Examples:
        "I want to go to the park" > "Let's go to the park" = 95
        "We went to the tall building" > "Skyscrapers are awesome" = 60
        "I want ice cream" > "the horses name is bob" = 0
        """

        human_prompt = f"""
        Item #1: {item_1}
        Item #2: {item_2}
        """

        llm_similarity = self.call_llm(
            system_prompt=system_prompt,
            human_prompt=human_prompt,
            model=self.similarity_model,
        )

        llm_similarity = int(llm_similarity)

        return llm_similarity

    def get_embedding(self, item):
        embedding = openai.Embedding.create(model="text-embedding-ada-002", input=item)
        return embedding["data"][0]["embedding"]

    def semantic_search(self, item: str) -> List[str]:
        """The goal is to return items which are semantically similar to the one that is provided
        We'll first do a rough pass of cosine similarity to get candidates.
        Then do a more thorough check with the LLM"""
        similarities = []

        # iterate through all existing items and check similarity

        # First, get the cosine similarities for all the items in the list
        cosine_similarities = [
            self.get_cosine_similarity(item, existing_item["formatted_name"])
            for existing_item in self.deduplicated_items_list
        ]

        # Then find the ones that are above your first pass threshold
        above_threshold_indexes = [
            i
            for i, sim in enumerate(cosine_similarities)
            if sim >= self.cosine_similarity_threshold
        ]

        # Then run through each item that was deemed similar via the cosine similarity and ask the LLM what it thinks
        for index in above_threshold_indexes:
            similar_item = self.deduplicated_items_list[index]["formatted_name"]
            llm_sim = int(self.get_llm_similarity(item, similar_item)) / 100
            print(
                f"Sim - LLM:{llm_sim}/Cos:{cosine_similarities[index]:.2f}, |{item}| & |{similar_item}|"
            )
            if llm_sim >= self.final_similarity_threshold:
                similarities.append(similar_item)

        if similarities:
            # Only returning top similarity for now to reduce complexity
            return sorted(similarities, key=lambda x: x[1], reverse=True)[0]
        else:
            return None


if __name__ == "__main__":
    sd = SemanticDeduplicator(
        similarity_background="""
            You are helping me deduplicate feature requests for a product.
            Please make sure to stay concise.
            Remove the first-person pronouns and focusing on the specific functionalities or improvements.
            Stripping away the "I" or "my" references to make the requests more general and applicable to a broader
            audience.
            Create clear and direct feature requests that can be easily understood and implemented by developers or
            relevant parties.
            Do not use punctuation
        """
    )

    sd.add_item("Please speed up your app, it is very slow")
    sd.add_item("I want dark mode")
    sd.add_item("I wish there was a darker version of your app")
    # sd.add_item("I wish there was a button to change my settings")
    # sd.add_item("How do I change my profile picture?")
    # sd.add_item("Your app is awesome! But I wish I could invite my friends easily")
    # sd.add_items(["I don't see a spot to put my credit card", "I can't figure out how to invite my friends"])
    sd.delete_item("users have been requesting dark mode")

    print("\nItems List")
    for i, item in enumerate(sd.deduplicated_items_list):
        print(
            f"""Item #{i + 1} \nFormatted Name: {item['formatted_name']} \nOld Names: {item['original_items_list']}
            \nOriginal Item Count: {item['num_original_items']}\n"""
        )
