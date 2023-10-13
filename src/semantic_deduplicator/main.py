import numpy as np
import openai
from typing import List
import os
from dotenv import load_dotenv
import warnings
import json
from .utils import call_llm, get_embedding

load_dotenv()

class DeduplicatedItem:
    def __init__(self, item_name, original_input=None, background_context=None):
        """
        This class represents a deduplicated item in the Semantic Deduplicator.

        Attributes:
            item_name (str): The name of the item.
            original_input (str): The original input string from which the item was extracted.
            background_context (str): The context in which the item is being consolidated.
            original_input_list (list): A list of original inputs. Initialized with the original input.
            formatted_name (str): The formatted name of the item, obtained by transforming the item name.
            item_embedding (np.array): The embedding of the formatted item name.
        """
        
        self.original_input_list = [original_input]
        self.name = self.transform_item_name(background_context, item_name=item_name)
        self.item_embedding = get_embedding(self.name)

    def update_item_name(self, background_context, new_item_name):
        """
        Updates the name of the item and its corresponding embedding.

        Args:
            background_context (str): The context in which the item is being consolidated.
            new_item_name (str): The new name for the item.
        """
        
        self.name = self.transform_item_name(background_context, new_item_name)
        self.update_item_embedding()
    
    def update_item_embedding(self):
        """
        Updates the embedding given a name string.

        Args: None
        """
        new_item_embedding = get_embedding(self.name)
        self.item_embedding = new_item_embedding

    def transform_item_name(self, background_context, item_name=None):
        """
        Takes the raw user input and outputs a clean name given the background context

        Args:
            background_context (str): The context in which the item is being consolidated.
            item_name (str): Optional, a string to transform. This defaults to the first item on the original_input_list
        """

        # We can upgrade this to function calling
        """A string that comes in might not be in a clear format. This function helps standardize names and extract requests"""
        system_prompt = f"""
        Your goal is to reword a user input according to their instructions.
        Their instructions will describe a desired goal or output and you should transform the phrase or item to the best of your ability

        % Start of user's background
        {background_context}
        % End of user's background

        Respond with nothing else besides the new item name.
        No not include any labels, or double-quotes
        Capitalize the first letter of your response
        """

        # Use the provided item_name if it's not None, otherwise use the first item from original_input_list
        item_to_transform = item_name if item_name is not None else self.original_input_list[0]

        human_prompt = f"""
        Here is my item: {item_to_transform}
        """

        new_item_name = call_llm(system_prompt=system_prompt, human_prompt=human_prompt)

        return new_item_name

    def __repr__(self):
        return f'DeduplicatedItem("{self.name}")'

class SemanticDeduplicator:
    def __init__(self, background_context="", llm_similarity_threshold=0.8, cosine_similarity_threshold=.75, openai_api_key = ''):
        """
        Initializes the SemanticDeduplicator class.

        Args:
            background_context (str): The context in which the items are being consolidated. Defaults to an empty string.
            llm_similarity_threshold (float): The final threshold for similarity. Defaults to 0.8.
            cosine_similarity_threshold (float): The threshold for cosine similarity. Defaults to 0.75.
            openai_api_key (str): The API key for OpenAI. Defaults to an empty string.
        """
        
        self.deduplicated_items_list = []
        self.cosine_similarity_threshold = cosine_similarity_threshold
        self.llm_similarity_threshold = llm_similarity_threshold
        self.background_context=background_context
        self.similarity_model = 'gpt-4'

        # If the API key is provided during initialization, use it. Else, get it from the environment variable.
        openai.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API key must be provided or set in the environment variable 'OPENAI_API_KEY'")
        
        if background_context=="":
            warnings.warn("The 'background_context' variable is empty. This is used to inform the language model what type of items it's parsing and extracting. It's recommended to provide context on your data for better results. See https://github.com/gkamradt/SemanticDeduplicator for more information")

    def add_item(self, item):
        """
        This method takes an item as input and adds it to the 'deduplicated_items_list'. If the item is similar to an existing item in the list, it merges the two items.
        """

        items = self.parse_items_from_raw_item(item)

        for extracted_item in items:
            # Create a DeduplicatedItem object for the extracted item
            potential_item = DeduplicatedItem(item_name=extracted_item,
                                              original_input=item,
                                              background_context=self.background_context)

            self._add_item_to_list(potential_item)
    
    def add_single_item(self, item):
        """
        This method takes a single item as input and adds it to the 'deduplicated_items_list'. 
        If the item is similar to an existing item in the list, it merges the two items.

        This function assumes there is only one 'interesting' point within your item
        Args:
            item (str): The item to be added to the 'deduplicated_items_list'.
        
        """

        # Create a DeduplicatedItem object for the item
        potential_item = DeduplicatedItem(item_name=item,
                                          original_input=item,
                                          background_context=self.background_context)

        self._add_item_to_list(potential_item)

    def _add_item_to_list(self, item):
        """
        This method takes a DeduplicatedItem and adds it to the 'deduplicated_items_list'. 
        If the list is empty, it adds the item directly. 
        If the list is not empty, it checks if the item is similar to an existing item in the list and merges them if necessary.
        """

        # Check to see if your items list has any data
        if len(self.deduplicated_items_list) == 0:
            self.add_item_to_empty_list(item)
        else:
            self.add_item_to_existing_list(item)

    def parse_items_from_raw_item(self, item):
        """
        There may be multiple requests in a single submission from the user.
        This splits them into distinct requests to be processed individually
        """

        system_prompt = f"""
            You are a bot that is part of a semantic item deduplicator.
            You will be given a submission from a user which may or may not contain multiple items.
            Your goal is to return a list of item(s) that you find in a users submission.

            Here is background on the items they are submitting
            % Start of background
            {self.background_context}
            % End of background

            Keep your responses to as close to what the user said as possible.
            If there is only one item present, only return exactly what the user said.
            """
        
        function_schema = [
            {
                "name": "extract_items_from_submission",
                "description": "Extract the items from the users submission",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "description": "Items listed within a users request",
                            "items": {
                                "type" : "string"
                            }
                        }
                    }
                }
            }
        ]

        list_of_items = call_llm(system_prompt=system_prompt,
                                 human_prompt=item,
                                 function_schema=function_schema,
                                 model="gpt-4-0613")

        return list_of_items

    def add_item_to_empty_list(self, item_to_add):
        self.add_item_to_deduplicated_list(item_to_add)

    def add_item_to_existing_list(self, item_to_add):
        # If your deduplist has data, then check to see if the item is similar to any of the existing items
        similar_items = self.get_similar_items(item_to_add)

        if len(similar_items) == 0:
            self.add_new_item_to_list(item_to_add)
        else:
            self.combine_item_with_existing_item(item_to_add, similar_items)

    def add_new_item_to_list(self, item_to_add):
        self.add_item_to_deduplicated_list(item_to_add)

    def combine_item_with_existing_item(self, item_to_add, similar_items):
        """
        This method combines a new item with an existing similar item in the 'deduplicated_items_list'. 
        It first selects the most similar item from the list of similar items. 
        Then it updates the name of the existing item with a combined name of the new item and the existing item. 
        It also extends the original input list of the existing item with the original input list of the new item.

        Args:
            item_to_add (DeduplicatedItem): The new item to be added.
            similar_items (list): A list of items that are similar to the new item.
        """
        
        # Just taking the top item to make it easy for now.
        # Will edit this later if it becomes an issue
        top_item = similar_items[0][0]

        # Get the index of the item you found similar in the existing list
        index_of_item_being_edited = next(i for i, item in enumerate(self.deduplicated_items_list) if item.name == top_item.name)
        
        new_item_name = self.get_combined_items_name(item_to_add=item_to_add, existing_item=top_item)

        top_item.update_item_name(background_context=self.background_context, new_item_name=new_item_name)
        top_item.original_input_list.extend(item_to_add.original_input_list)
        
    def add_item_to_deduplicated_list(self, item_to_add):
        self.deduplicated_items_list.append(item_to_add)
    
    def add_single_items(self, items: List[str]):
        """
        This method takes a list of items as input and adds each item to the 'deduplicated_items_list'. 
        If an item is similar to an existing item in the list, it merges the two items.

        Args:
            items (List[str]): The list of new items to be added.
        """
        
        for item in items:
            self.add_single_item(item)

    def get_combined_items_name(self, item_to_add, existing_item):
        """
        This method combines the names of a new item and an existing similar item.
        It uses the Language Model to generate a new name that incorporates information from both items.

        Args:
            item_to_add (DeduplicatedItem): The new item to be added.
            existing_item (DeduplicatedItem): The existing item that is similar to the new item.

        Returns:
            new_item_name (str): The combined name of the new item and the existing item.
        """        

        system_prompt = f"""
        Your goal is to combine two different similar items together. They have been deemed similar and should be comebined.
        Example: "I went to the park" & "I went to outside" > "I went outside"
        Example: "I want dark mode" & "I want two modes, light and dark" > "I want dark mode"

        Make sure you lose minimal information about the two items.

        Here is background information from the user about the items.
        Make sure to listen to the user and take their context into account.

        % Start of background
        {self.background_context}
        % End of background

        Respond with nothing else besides the new item name.
        No not include any labels, or double-quotes
        """

        human_prompt = f"""
        New Item: {item_to_add.name}
        Existing Item: {existing_item.name}
        """

        new_item_name = call_llm(system_prompt=system_prompt, human_prompt=human_prompt)

        return new_item_name

    def delete_item_from_string(self, item_string):
        item = DeduplicatedItem(item_name=item_string, background_context=self.background_context)

        similarities = self.get_similar_items(item)

        if len(similarities) == 0:
            pass

        else:
            top_item = similarities[0][0]

            index_of_item_being_deleted = next(i for i, item in enumerate(self.deduplicated_items_list) if item.name == top_item.name)

            self.deduplicated_items_list.pop(index_of_item_being_deleted)
    
    def cosine_similarity(self, item, existing_item):
        # Calculate the dot product of the two vectors
        dot_product = np.dot(item.item_embedding, existing_item.item_embedding)
        
        # Calculate the norms of each vector
        norm_1 = np.linalg.norm(item.item_embedding)
        norm_2 = np.linalg.norm(existing_item.item_embedding)
        
        # Calculate the cosine similarity
        cosine_similarity = dot_product / (norm_1 * norm_2)
        
        return cosine_similarity

    def get_cosine_similarity(self, item, existing_item):
        cosine_similarity_score = self.cosine_similarity(item, existing_item)
        
        return cosine_similarity_score

    def get_llm_similarity(self, item_1, item_2):
        """
        This method calculates the semantic similarity between two items using a Language Model.
        It generates a system prompt and a human prompt based on the names of the two items, 
        and then calls the Language Model to get a similarity score.

        Args:
            item_1 (DeduplicatedItem): The first item.
            item_2 (DeduplicatedItem): The second item.

        Returns:
            llm_similarity (int): The semantic similarity score between the two items, as determined by the Language Model.
        """
        
        system_prompt = f"""
        Your goal is to give a rating as to how semantically similar to items or phrases are together.
        You will be given two phrases.
        Words which are interchangable should be considered similar. Ex: Awesome, cool, great, wonderful are all similar

        Here is background information from the user about the items.
        Make sure to listen to the user and take their context into account.
        
        % Start of background
        {self.background_context}
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
        Item #1: {item_1.name}
        Item #2: {item_2.name}
        """

        llm_similarity = call_llm(system_prompt=system_prompt,
                                      human_prompt=human_prompt,
                                      model=self.similarity_model)
        
        llm_similarity = int(llm_similarity)

        return llm_similarity
     
    def get_similar_items(self, item: DeduplicatedItem) -> List[DeduplicatedItem]:
        """
        The goal is to return items which are semantically similar to the one that is provided
        We'll first do a rough pass of cosine similarity to get candidates.
        Then do a more thorough check with the LLM
        """
        similarities = []

        # iterate through all existing items and check similarity

        # First, get the cosine similarities for all the items in the list
        cosine_similarities = [self.get_cosine_similarity(item, existing_item) for existing_item in self.deduplicated_items_list]

        # Then find the ones that are above your first pass threshold
        above_threshold_indexes = [i for i, sim in enumerate(cosine_similarities) if sim >= self.cosine_similarity_threshold]
        
        # Then run through each item that was deemed similar via the cosine similarity and ask the LLM what it thinks
        for index in above_threshold_indexes:
            similar_item = self.deduplicated_items_list[index]
            similar_item_name = similar_item.name
            llm_sim = int(self.get_llm_similarity(item, similar_item)) / 100
            if llm_sim >= self.llm_similarity_threshold:
                # Append a tuple with your similar item and it's similarity score
                similarities.append((similar_item, llm_sim))
        
        # Return the similar items in descending order of similarity (most similar at the top)
        return sorted(similarities, key=lambda x: x[1], reverse=True)
    
    def get_formatted_deduplicated_list(self, get_type="string_list"):
        """
        Pretty print the list contents
        Args:
            get_type (str): The type of print format. Defaults to "string_list".
                "string_list": Joins the items together in a comma separated string
                "dict_list": Prints the list of deduplicated items as a list of dictionaries, with each dictionary representing an item and the original values as a list of strings
                "json": Prints the list of deduplicated items in JSON format.
        """
        if get_type == "string_list":
            return ', '.join([item.name for item in self.deduplicated_items_list])

        elif get_type == "dict_list":
            return [{'Formatted Name': item.name, 'Original Names': item.original_input_list} for item in self.deduplicated_items_list]

        elif get_type == "json":
            return json.dumps([{'Formatted Name': item.name, 'Original Names': item.original_input_list} for item in self.deduplicated_items_list])

        else:
            raise ValueError(f"Invalid get_type: {get_type}. Expected one of: 'string_list', 'dict_list', 'json'")