# Coding Challenge 

## Background

Dr Crop Community is a social network of plant experts, supporting each other 
in diagnosing plant diseases. Each expert has a unique id, a list of plant 
species (topics) they can give advice on and a list of other experts they
follow:

```
------------------------------------
  PlantExpert
------------------------------------
    uid:          String
    plants:       List[String]
    following:    List[String]
------------------------------------
  fetch(uid: String): PlantExpert
------------------------------------
```

The `fetch(uid)` API is already implemented and available in your Python SDK
(`plantix.py`). Feel free to re-implement this code if you need to use a 
different programming language.


## The challenge

Suppose an expert with `uid="0"` exists. Can you find what topics (plants) 
are covered by the experts in his/her entire network of connections 
(any degree)?

1. Implement a new SDK method in `plantix.PlantixApiClient`, which returns 
   a sorted `Tuple[String]` of the `n` most covered plants in the network of 
   experts reachable from expert `start`. For example, if there are 5 experts 
   on `tomato`, 3 on `banana`, and 10 on `cucumber` - all reachable from user 
   with `uid="3"`, this method should return:
   
   ```
   >>> from DrCrop import *
   >>> DrCropClient().find_topics(start="3", n=2)
   ('cucumber', 'tomato')
   ```
   
   in this order.
2. Write unit- and integration tests for your solution.
3. Run your solution with input `start=0, n=3`. That is, calculate the top 3 
   most covered plant species in the network of experts reachable from `uid=0`.
4. Analyze the running time and memory complexity of your solution. Consider 
   best- and worst-cases.
5. Write a small design doc to explain the problem and your approach to solving
   it. Add your `O()` analysis in there too.
6. Type in the output from (3) as an answer in your application form and 
   attach a single zip archive containing all of your source code (1-2) and 
   design doc (3-5) for review. For example, if your program produced the 
   output `('cucumber', 'tomato')`, you need to type in `cucumber, tomato` in
   the application form and attach a zip file with the SDK, your code, tests,
   and design doc. 


## Requirements

- This is a small task. If you find yourself writing a lot of code, you might 
  want to consider a different approach. 
- Use any modern language you like; however we only provide an "SDK" for 
  Python. You can use the standard library of your language, but no other 
  packages. Your code should compile without any dependencies. 
- Write production-quality, correct, clean, maintainable, testable, tested, 
  documented and scalable code. 
- Feel free to remodel `DrCropClient`, add new functions, methods, 
  properties or classes if necessary. You can't modify `DrCropExpert` however.
- You do not have unlimited amounts of RAM. Your solution should scale.
- Format your code the way you normally would when working in a team. If using 
  Python, follow PEP8 and provide type annotations and docstrings.# Here are your Instructions
