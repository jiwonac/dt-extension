
"""
Represents a data point, to be used in a data source. 
Contains a group identity (an integer) and arbitrary extra data. 
"""

class DataPoint:
    def __init__(self, group, data):
        """
        @params
            group: an integer between 0 and m - 1
            data: arbitrary data to be stored in this data point, must be
                  hashable to allow the data point to be hashable
        """
        self.group = group
        self.data = data
    
    def __str__(self):
        return "(G" + str(self.group) + ", " + str(self.data) + ")"

    def __repr__(self):
        return (str(self))

    def __hash__(self):
        return hash(self.data)

# Test cases
if __name__ == '__main__':
    a = DataPoint(0, (1.5, 2.5, 3.5))
    b = DataPoint(1, (3.0, 2.0, 1.0))
    print(a, b)
    print(hash(ad))