import os

directoryName = "coverart/1208901-1209241"

def moveImage(imageName, directory):
  global directoryName
  os.rename(directoryName + "/" + image, "indexed-images/" + fileSubStr + "/" + image)

imagesInDir = os.listdir(directoryName)

for image in imagesInDir:
  fileSubStr = image[:2]
  if os.path.exists("indexed-images/" + fileSubStr):
    moveImage(image, fileSubStr)
  else:
    os.makedirs("indexed-images/" + fileSubStr)
    moveImage(image, fileSubStr)
