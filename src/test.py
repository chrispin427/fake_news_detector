from similarity_checker import calculate_similarity

text1 = """
The government announced a new education policy today.
"""

text2 = """
Today the government introduced a new education policy.
"""

score = calculate_similarity(
    text1,
    text2
)

print("Similarity:", score)