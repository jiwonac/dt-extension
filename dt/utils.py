import random

def argmax(dictionary):
    """
    @params
        dictionary: a collection of item to numeric value mappings
    @returns the key with the highest numeric value, ties broken randomly
    """
    max_value = max(dictionary.values())
    max_items = [ key for key in dictionary.keys() 
                  if dictionary[key] >= max_value]
    return random.choice(max_items)

# Test case
if __name__ == '__main__':
    grades = {
        'Alice': 90,
        'Bob': 100,
        'Catherine': 95,
        'Danny': 100,
        'Evelyn': 80
    }
    print(argmax(grades))