# Example: reuse your existing OpenAI setup
from typing import Optional
from openai import OpenAI
import asyncio

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


SYSMTEM_PROMPT = f"""I am an expert compuer programmer. I am able to generate function code in the given programming language when given a natural language description of the function. 
I am able to handle a variety of programming languages, including Python, JavaScript, PHP.

Prompt:
Given a natural language description of a function, I can generate function code in the given programming language. The function description should include the following information:

The name of the function
The return type of the function
The input parameters of the function
The body of the function
The code should be well-structured and easy to understand. It should also be efficient and idiomatic for the given programming language.

Example:
Generate a python function called sum_two_numbers which takes two numbers as parameters and returns the sum of the two numbers.

output:
```python
def sum_two_numbers(num1, num2):
  return num1 + num2
```

Additional Requirements:
I am able to handle a variety of natural language descriptions, including:

Formal descriptions that use precise language and terminology
Informal descriptions that use more natural language and may contain errors or ambiguities
Incomplete descriptions that may lack some information about the function
The agent should be able to infer the missing information from the context of the description and generate complete and accurate function code.

Javascript functions should follow this format: exports.functionName = ()=>

Evaluation Criteria:

The agent will be evaluated on the following criteria:

Accuracy: The generated code should be correct and match the natural language description of the function.
Completeness: The generated code should be complete and include all of the necessary statements and expressions.
Readability: The generated code should be easy to understand and follow, even for someone who is not an expert in the programming language.
Efficiency: The generated code should be efficient and use the best practices for the given programming language.
"""

async def generate_function(description: str, language: Optional[str] = None, function_name: Optional[str] = None):
    prompt = f"""Description:\n{description}
    """
    if language:
        prompt += f"""\nlanguage:\n{language}
        """
        
    if language:
        prompt += f"""\nfunction_name:\n{function_name}
        """

    completion = client.chat.completions.create(
    model="local-model", # this field is currently unused
    messages=[
        {"role": "system", "content": SYSMTEM_PROMPT},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    )

    return completion.choices[0].message.content

if __name__ == '__main__':
    description = input('Description> ')
    language = input('language> ')
    result = asyncio.run(generate_function(description, language))
    print(result)