# Semantic Deduplication

One of the most annoying parts of gathering items for a list is **deduplicating them**. Let's fix this

```
    sd = SemanticDeduplicator(similarity_background="You are helping me deduplicate feature requests for a product")

    sd.add_item("Please speed up your app, it is very slow")
    sd.add_item("I want dark mode")
    sd.add_item("I wish there was a darker version of your app")
    
    # >> Improve application speed, Implement Dark Mode
```

Under the hood this library uses OpenAI's API for reviewing the semantic meaning of each list item and deciding if they should be consolidated or not

[![Semantic Deduplicator Demo](https://ih0.redbubble.net/image.25011287.7046/flat,500x500,075,f.u1.jpg)](https://www.youtube.com/watch?v=QXprR7QpWDQ)