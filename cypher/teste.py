import sys

print('Number of arguments:', len(sys.argv), 'arguments.')

print('Argument List:', str(sys.argv[1]))

for index in range(len(sys.argv)):
    print('Number of arguments:', index, 'arguments.')
