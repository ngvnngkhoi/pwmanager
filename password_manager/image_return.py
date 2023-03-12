from google_images_download import google_images_download


response = google_images_download.googleimagesdownload()

args = {"keywords":"dog","limit":2,"print_urls":True}


paths = response.download(args)

print(paths)

