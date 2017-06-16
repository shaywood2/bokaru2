# Function to generate a matrix of dates based on two lists of participants
def generate_date_matrix_two_groups(group_a, group_b):
    size = max(len(group_a), len(group_b))
    matrix = [[0 for x in range(size)] for y in range(size)]

    for i in range(size):
        for j in range(size):
            index = (i + j) % size
            if index < len(group_b):
                matrix[i][j] = group_b[index]
            print (matrix[i][j])
        print ('---')

    return matrix

generate_date_matrix_two_groups([1, 2, 3, 4], [5, 6, 7])
