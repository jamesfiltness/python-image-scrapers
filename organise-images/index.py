import os

def moveImage(imageName, directory):
  os.rename("images/" + image, "indexed-images/" + fileSubStr + "/" + image)

imagesInDir = os.listdir('images')

for image in imagesInDir:
  fileSubStr = image[:2]
  if os.path.exists(fileSubStr):
    moveImage(image, fileSubStr)
  else:
    os.makedirs("indexed-images/" + fileSubStr)
    moveImage(image, fileSubStr)
