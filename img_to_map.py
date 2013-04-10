import pygame, sys

argv = sys.argv[1:]

# Need both arguments

# Load pygame and the image
pygame.init()
image = pygame.image.load(argv[0])

# Create the map file
if len(argv) > 1:
    outname = argv[1]
else:
    outname = argv[0].split('.')[0] + '.map'
out = open(outname, 'w')

# Go through the image
for y in range(image.get_height()):
    for x in range(image.get_width()):
        out.write('{} '.format(image.get_at_mapped((x, y))))
    out.write('\n')
out.close()
