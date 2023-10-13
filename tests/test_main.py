from semantic_deduplicator import SemanticDeduplicator, DeduplicatedItem

def test_simple_deduplication_product_feedback():
    sd = SemanticDeduplicator(
    background_context="""
        You are helping me deduplicate feature requests for a product.
        Please make sure to stay concise.
        Remove the first-person pronouns and focusing on the specific functionalities or improvements.
        Stripping away the "I" or "my" references to make the requests more general and applicable to a broader audience.
        Create clear and direct feature requests that can be easily understood and implemented by developers or relevant parties.
        Do not use puncutation
    """
    )
    
    sd.add_single_item("I want dark mode")
    sd.add_single_item("I wish there was a darker version of your app")

    # testing to make sure these items were actually consolidated
    assert len(sd.deduplicated_items_list)==1

def test_simple_delete_product_feedback():
    sd = SemanticDeduplicator(
    background_context="""
        You are helping me deduplicate feature requests for a product.
        Please make sure to stay concise.
        Remove the first-person pronouns and focusing on the specific functionalities or improvements.
        Stripping away the "I" or "my" references to make the requests more general and applicable to a broader audience.
        Create clear and direct feature requests that can be easily understood and implemented by developers or relevant parties.
        Do not use puncutation
    """
    )
    
    sd.add_single_item("I want dark mode")
    sd.delete_item_from_string("I wish there was a darker version of your app")

    # Making sure the item was removed successfully
    assert len(sd.deduplicated_items_list)==0

def test_simple_deduplication_groceries():

    sd = SemanticDeduplicator(
        background_context="""
            You are a helpful bot that consolidates grocery items for me as I'm about to go to the store.
            Combine like items
            Do not combine items based on their use case. Your focus is to combine them based on the item.
        """
    )

    sd.add_single_item("Berries")
    sd.add_single_item("Milk for cereal")
    sd.add_single_item("Milk for drinking")

    assert len(sd.deduplicated_items_list)==2

def test_add_multitem_deduplication_item():

    sd = SemanticDeduplicator(
        background_context="""
            You are a helpful bot that consolidates grocery items for me as I'm about to go to the store.
            Combine like items
            Do not combine items based on their use case. Your focus is to combine them based on the item.
        """
    )

    sd.add_item("Berries, milk and meat")

    assert len(sd.deduplicated_items_list)==3

def test_add_deduplication_items():

    sd = SemanticDeduplicator(
        background_context="""
            You are a helpful bot that consolidates grocery items for me as I'm about to go to the store.
            Combine like items
            Do not combine items based on their use case. Your focus is to combine them based on the item.
        """
    )

    sd.add_single_items(["Berries", "milk",  "meat"])

    assert len(sd.deduplicated_items_list)==3

def test_simple_duplicated_item_create():
    di = DeduplicatedItem("My test item")
    assert len(di.item_embedding) > 0